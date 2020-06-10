from django.test import TestCase

from core.models import FaqItem


class CoreFaqTests(TestCase):
    def test_faq_model(self):
        fi1 = FaqItem.objects.create(question='A question', answer='An answer')
        fi2 = FaqItem.objects.create(question='A question', answer='An answer')
        fi3 = FaqItem.objects.create(question='A question', answer='An answer')

        # sanity check
        self.assertEquals(fi1.question, 'A question')
        self.assertEquals(fi1.answer, 'An answer')

        # it should have created 3 items
        self.assertEquals(FaqItem.objects.count(), 3)

        # soft delete test
        fi3.disabled = True
        fi3.save()

        self.assertEquals(FaqItem.objects.count(), 2)
