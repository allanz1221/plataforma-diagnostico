from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.views.generic.base import View

from support.email import send_new_ticket_posted, send_new_admin_comment_posted, send_ticket_solved, send_ticket_working
from support.forms import CommentForm, TicketForm
from support.messages import get_comment_success_message, get_send_email_success_message, get_comment_error_message, \
    get_update_status_success_message, get_update_status_error_message, get_exam_reset_success_message, \
    get_exam_reset_error_message
from support.models import Ticket
from support.models import SOLVED, WORKING, PENDING
from support.services import get_exam_results, action_reset_exam


def get_ticket_detail(pk):
    """Get ticket detail. The query for the detailed view"""
    return Ticket.objects.get(pk=pk)


class ActionBase(LoginRequiredMixin, View):
    """
    Support Ticket Action Base. Base class for admin actions.
    """
    def get(self, request, *args, **kwargs):
        """Get should be disabled"""
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Only available for admins"""
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SupportHomeView(LoginRequiredMixin, ListView):
    """
    Support Home View. ListView of all the tickets posted by the user.
    """
    model = Ticket
    template_name = 'support_home.html'
    paginate_by = 10
    ordering = ('-created_at',)

    def get_queryset(self):
        """Replaces the queryset so an admin can see all the tickets created by all the users"""
        queryset = super(SupportHomeView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset


class SupportTicketCreateView(LoginRequiredMixin, CreateView):
    """
    Support Ticket Create View. Create view for a ticket instance.
    """
    form_class = TicketForm
    template_name = 'support_ticket_create.html'
    login_url = 'login'

    def get_success_url(self):
        """Get success url"""
        send_new_ticket_posted(self.object)  # sends an email each time a ticket is created
        return super().get_success_url()

    def form_valid(self, form):
        """Form valid"""
        form.instance.user = self.request.user  # attaches the user to the form
        return super().form_valid(form)


class SupportTicketDetailView(LoginRequiredMixin, View):
    """
    Support Ticket Detail View. Custom view where the detailed ticket info is displayed, and where the users can post
    comments.
    """
    def get(self, request, *args, **kwargs):
        """Get. It displays the detailed ticket info and all the comments"""
        ticket = get_ticket_detail(kwargs['pk'])
        return render(request, 'support_ticket_detail.html', {
            'ticket': ticket,  # queried ticket
            'comment_form': CommentForm(),  # comment form
            'result': get_exam_results(ticket.user)
        })

    def dispatch(self, request, *args, **kwargs):
        """Dispatch. So a user can only see his/her tasks"""
        ticket = get_ticket_detail(kwargs['pk'])
        if not request.user.is_staff and ticket.user != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PostCommentActionView(LoginRequiredMixin, View):
    """
    Post Comment Action View. Handles new comments.
    """
    def post(self, request, *args, **kwargs):
        """Post comment"""
        ticket = get_ticket_detail(kwargs['pk'])

        # check if the user can post a comment
        if ticket.status != SOLVED:
            comment_form = CommentForm(request.POST, request.FILES)

            # validate the form
            if comment_form.is_valid():
                f = comment_form.save(commit=False)
                f.user = request.user  # attach the user
                f.ticket = ticket  # attach the ticket
                f.save()  # now save
                messages.success(request, get_comment_success_message())

                # if a staff member posted a comment it should send an email to the user
                if request.user.is_staff:
                    send_new_admin_comment_posted(ticket, request.POST['text'])
                    messages.info(request, get_send_email_success_message(ticket.user))
            else:
                messages.error(request, get_comment_error_message())
                # for e in comment_form.errors:
                #    messages.error(request, comment_form.errors[e])

        return redirect('support:ticket_detail', ticket.id)

    def dispatch(self, request, *args, **kwargs):
        """Dispatch. So a user can only see his/her tasks"""
        ticket = get_ticket_detail(kwargs['pk'])
        if not request.user.is_staff and ticket.user != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ChangeStatusActionView(ActionBase):
    """
    Change Status Action View. Admin action, changes the status of the ticket.
    """
    def post(self, request, *args, **kwargs):
        """Handles the status change action"""
        ticket = get_ticket_detail(kwargs['pk'])
        try:
            ticket.status = request.POST['status']
            ticket.save()
            messages.success(request, get_update_status_success_message())

            if request.POST['status'] == SOLVED:
                send_ticket_solved(ticket)  # send an email with the solved template
                messages.info(request, get_send_email_success_message(ticket.user))

            if request.POST['status'] == PENDING:
                send_ticket_working(ticket)  # send an email with the "working on it" template
                messages.info(request, get_send_email_success_message(ticket.user))

        except Exception as e:
            messages.error(request, get_update_status_error_message(e))

        return redirect('support:ticket_detail', ticket.id)


class ResetExamActionView(ActionBase):
    """
    Reset Exam Action View.
    """
    def post(self, request, *args, **kwargs):
        """Handles the reset action"""
        ticket = get_ticket_detail(kwargs['pk'])
        if action_reset_exam(ticket.user):
            messages.success(request, get_exam_reset_success_message())
        else:
            messages.error(request, get_exam_reset_error_message())
        return redirect('support:ticket_detail', ticket.id)
