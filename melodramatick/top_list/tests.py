from django.test import TestCase

from .views import TopListView


class TopListViewTestCase(TestCase):
    fixtures = ["testtick_composer.json", "testtick_top_list.json", "user.json", "testtick_work.json",
                "testtick_testitem.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.view = TopListView()
        self.view.setup(self.request)

    def test_get_table_data(self):
        table_data = self.view.get_table_data()
        self.assertListEqual(
            list(table_data.values('max_position', 'list_work_count').order_by('id')),
            [{'max_position': 2, 'list_work_count': 2},  # <List: Top test items - Example Dot Com>
             {'max_position': 1, 'list_work_count': 1}]  # <List: Another Test List - Example Dot Com>
        )
