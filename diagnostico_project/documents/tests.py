from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from documents.models import Category, Document


def _get_test_file():
    file = SimpleUploadedFile(name='test_file',
                              content=open('./static/img/placeholder150.jpg', 'rb').read(),
                              content_type='image/jpeg')
    return file


def _get_wrong_type_test_file():
    file = SimpleUploadedFile(name='wrong_test_file',
                              content=open('./static/img/ues-navbar-logo.png', 'rb').read(),
                              content_type='image/png')
    return file


class DocumentsBaseTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='ramon.parra@ues.mx',
            password='secret'
        )
        self.client.login(username=self.user.username, password='secret')


class DocumentsModelTest(DocumentsBaseTest):
    def test_categories(self):
        # It should have a name and a description
        category = Category.objects.create(name='A name', description='A description')
        self.assertIsNotNone(category)
        self.assertEquals(category.name, 'A name')
        self.assertEquals(category.description, 'A description')

        # When it's first created, it should have 0 attached documents
        self.assertEquals(category.document_set.count(), 0)

        # Unless we start creating documents
        file = _get_test_file()
        doc1 = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        doc2 = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')

        self.assertEquals(category.document_set.count(), 2)

        # If disabled, it should be deleted
        category.disabled = True
        category.save()

        categories = Category.objects.all()
        self.assertEquals(categories.count(), 0)

    def test_documents(self):
        file = _get_test_file()
        category = Category.objects.create(name='A name', description='A description')
        doc = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')

        self.assertEquals(doc.comment, 'A comment')
        self.assertEquals(doc.user.id, self.user.id)

        # If disabled, it should be deleted
        doc.disabled = True
        doc.save()

        docs = Document.objects.all()
        self.assertEquals(docs.count(), 0)

    def test_categories_get_by_user(self):
        category = Category.objects.create(name='A name', description='A description')
        file = _get_test_file()
        another_user = get_user_model().objects.create_user(
            username='testuser2',
            email='ramon.parra@ues.mx',
            password='secret'
        )

        # user 1 uploaded 3 documents
        doc = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')

        # user 2 uploaded 5 documents
        doc = Document.objects.create(file=file, user=another_user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=another_user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=another_user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=another_user, category=category, comment='A comment')
        doc = Document.objects.create(file=file, user=another_user, category=category, comment='A comment')

        self.assertEquals(category.get_documents_by_user(self.user).count(), 3)
        self.assertEquals(category.get_documents_by_user(another_user).count(), 5)


class DocumentsViewsTest(DocumentsBaseTest):
    class MockRequest:
        def __init__(self, post={}):
            self.POST = post

        def keys(self):
            return self.POST.keys()

        def get(self, key):
            return self.POST.get(key)

    def test_delete_document_view(self):
        category = Category.objects.create(name='A name', description='A description')
        file = _get_test_file()

        # user 1 uploaded 3 documents
        doc1 = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        doc2 = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        doc3 = Document.objects.create(file=file, user=self.user, category=category, comment='A comment')
        self.assertEquals(category.get_documents_by_user(self.user).count(), 3)

        # now, it should delete the last one when a post is made to /documents/delete
        response = self.client.post(reverse('documents:delete'), {
            'document_id': doc3.id
        })
        self.assertRedirects(response, reverse('documents:home'))  # it should always redirect to home

        # and it should have now only two documents
        self.assertEquals(category.get_documents_by_user(self.user).count(), 2)

        # if another document_id is posted, it should redirect to home (with an error message), and it should have the
        # same number of documents
        response = self.client.post(reverse('documents:delete'), {
            'document_id': '100'
        })
        self.assertRedirects(response, reverse('documents:home'))
        self.assertEquals(category.get_documents_by_user(self.user).count(), 2)

        # if another user tries to make a post with a document_id that doesn't belong to him/her, it should return an
        # error message
        another_user = get_user_model().objects.create_user(
            username='testuser2',
            email='ramon.parra@ues.mx',
            password='secret'
        )

        self.client.login(username=another_user.username, password='secret')
        self.client.post(reverse('documents:delete'), {
            'document_id': doc2.id
        })
        self.assertRedirects(response, reverse('documents:home'))
        self.assertEquals(category.get_documents_by_user(self.user).count(), 2)
