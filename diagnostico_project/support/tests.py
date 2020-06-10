from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from support.models import Task, Ticket, Comment
from support.models import PENDING, WORKING, SOLVED


class SupportBaseTest(TestCase):
    def setUp(self):
        # create an admin
        self.admin = get_user_model().objects.create_superuser(
            username='testadmin',
            email='ramon.parra@ues.mx',
            password='secret'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='ramon.parra90@gmail.com',
            password='secret'
        )


class SupportModelsTest(SupportBaseTest):
    def test_task_model(self):
        # create a new task
        task = Task.objects.create(title='A task')

        # sanity check
        self.assertEquals(task.title, 'A task')
        self.assertEquals(Task.objects.count(), 1)

        # check soft delete
        task.disabled = True
        task.save()

        self.assertEquals(Task.objects.count(), 0)

    def test_ticket_model(self):
        # required to create a ticket
        task = Task.objects.create(title='A task')
        ticket = Ticket.objects.create(user=self.user,
                                       task=task,
                                       title='A ticket',
                                       description='A description')
        ticket.save()

        # sanity check
        self.assertEquals(ticket.user.id, self.user.id)
        self.assertEquals(ticket.task.id, task.id)
        self.assertEquals(ticket.title, 'A ticket')
        self.assertEquals(ticket.description, 'A description')

        # check defaults
        self.assertEquals(ticket.status, PENDING)

        # check soft delete
        self.assertEquals(Ticket.objects.count(), 1)

        ticket.disabled = True
        ticket.save()

        self.assertEquals(Ticket.objects.count(), 0)

    def test_comment_model(self):
        task = Task.objects.create(title='A task')
        ticket = Ticket.objects.create(user=self.user,
                                       task=task,
                                       title='A ticket',
                                       description='A description')

        c1 = Comment.objects.create(user=self.user, ticket=ticket, text='User comment 1')
        c2 = Comment.objects.create(user=self.user, ticket=ticket, text='User comment 2')
        c3 = Comment.objects.create(user=self.user, ticket=ticket, text='User comment 3')

        c4 = Comment.objects.create(user=self.admin, ticket=ticket, text='Admin comment 1')
        c5 = Comment.objects.create(user=self.admin, ticket=ticket, text='Admin comment 2')
        c6 = Comment.objects.create(user=self.admin, ticket=ticket, text='Admin comment 3')

        # check comments number
        self.assertEquals(ticket.comments.all().count(), 6)


class SupportViewsTest(SupportBaseTest):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(title='A task')
        self.t1 = Ticket.objects.create(user=self.admin,
                                        task=self.task,
                                        title='Admin task',
                                        description='A description')
        self.t2 = Ticket.objects.create(user=self.user,
                                        task=self.task,
                                        title='User task',
                                        description='A description')

    def test_support_home_view(self):
        # sanity check
        self.client.login(username=self.admin.username, password='secret')
        request = self.client.get(reverse('support:home'))
        self.assertEquals(request.status_code, 200)

    def test_support_ticket_create_view(self):
        # sanity check
        self.client.login(username=self.admin.username, password='secret')
        request = self.client.get(reverse('support:ticket_create'))
        self.assertEquals(request.status_code, 200)

    def test_support_ticket_detail_view(self):
        # an admin can see any ticket
        self.client.login(username=self.admin.username, password='secret')
        request = self.client.get(reverse('support:ticket_detail', kwargs={'pk': self.t1.id}))
        self.assertEquals(request.status_code, 200)

        request = self.client.get(reverse('support:ticket_detail', kwargs={'pk': self.t2.id}))
        self.assertEquals(request.status_code, 200)

        # a user can only see his/her tickets
        self.client.login(username=self.user.username, password='secret')
        request = self.client.get(reverse('support:ticket_detail', kwargs={'pk': self.t1.id}))
        self.assertNotEquals(request.status_code, 200)

        request = self.client.get(reverse('support:ticket_detail', kwargs={'pk': self.t2.id}))
        self.assertEquals(request.status_code, 200)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_post_comment_action_view(self):
        self.client.login(username=self.admin.username, password='secret')

        # a user can post comments here
        self.client.post(reverse('support:comment', kwargs={'pk': self.t2.id}), data={
            'action_type': 'post_comment',
            'ticket_id': self.t2.id,
            'text': 'A comment!'
        })
        self.client.post(reverse('support:comment', kwargs={'pk': self.t2.id}), data={
            'action_type': 'post_comment',
            'ticket_id': self.t2.id,
            'text': 'Another comment!'
        })
        t2 = Ticket.objects.get(id=self.t2.id)
        self.assertEquals(t2.comments.count(), 2)

        # unless the ticket is marked as solved
        self.t2.status = SOLVED
        self.t2.save()

        self.client.post(reverse('support:ticket_detail', kwargs={'pk': self.t2.id}), data={
            'action_type': 'post_comment',
            'ticket_id': self.t2.id,
            'text': 'Yet another comment!'
        })
        t2 = Ticket.objects.get(id=self.t2.id)
        self.assertNotEquals(t2.comments.count(), 3)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_change_status_action_view(self):
        # post data for this view
        post_data = {
            'status': SOLVED
        }

        # a user should not be able to change the ticket status
        self.assertEquals(self.t2.status, PENDING)
        self.client.login(username=self.user.username, password='secret')
        self.client.post(reverse('support:change_status', kwargs={'pk': self.t2.id}), post_data)
        t2 = Ticket.objects.get(id=self.t2.id)
        self.assertNotEquals(t2.status, SOLVED)
        self.assertEquals(t2.status, PENDING)

        # only an admin can do it
        self.client.login(username=self.admin.username, password='secret')
        self.client.post(reverse('support:change_status', kwargs={'pk': self.t2.id}), post_data)
        t2 = Ticket.objects.get(id=self.t2.id)
        self.assertEquals(t2.status, SOLVED)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_reset_exam_action_view(self):
        # post data for this view
        post_data = {}

        # a user should not be able to post anything to this view
        self.client.login(username=self.user.username, password='secret')
        request = self.client.post(reverse('support:change_status', kwargs={'pk': self.t2.id}), post_data)
        self.assertEquals(request.status_code, 403)

        # only an admin
        self.client.login(username=self.admin.username, password='secret')
        request = self.client.post(reverse('support:change_status', kwargs={'pk': self.t2.id}), post_data)
        self.assertNotEquals(request.status_code, 403)
