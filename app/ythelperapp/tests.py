from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import *
from .forms import UpdateUserForm

import datetime

class user_data_storage_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )
        user_data_storage.objects.create(user=User.objects.get(username="testUser"))

    def test_user_data_storage(self):
        """Save history option works correctly"""
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUser"))
        
        storage.save_history = True
        storage.save()
        self.assertEqual(storage.save_history, True)

        storage.save_history = False
        storage.save()
        self.assertEqual(storage.save_history, False)


class download_history_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )
        user_data_storage.objects.create(user=User.objects.get(username="testUser"))

    def test_download_history(self):
        """Saving downloaded videos works correctly"""
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUser"))
        
        if storage.save_history:
            download_history_item.objects.create(
                user = User.objects.get(username="testUser"),
                title = "Example Of Youtube Video Title",
                link = "https://www.youtube.com",
                thumbnail_url = "https://www.youtube.com"
            )

        item_in_history = download_history_item.objects.get(id=1)

        self.assertIsNotNone(item_in_history)


class prompts_history_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )
        user_data_storage.objects.create(user=User.objects.get(username="testUser"))

    def test_prompts_history(self):
        """Saving prompts works correctly"""
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUser"))
        
        if storage.save_history:
            prompts_history_item.objects.create(
                user = User.objects.get(username="testUser"),
                title = "Example Of Youtube Video Title",
                link = "https://www.youtube.com",
            )

        item_in_history = prompts_history_item.objects.get(id=1)

        self.assertIsNotNone(item_in_history)


class filtered_comments_history_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )
        user_data_storage.objects.create(user=User.objects.get(username="testUser"))

    def test_filtered_comments_history(self):
        """Saving filtered comments works correctly"""
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUser"))
        
        if storage.save_history:
            filtered_comments_history_item.objects.create(
                user = User.objects.get(username="testUser"),
                title = "Example Of Youtube Video Title",
                link = "https://www.youtube.com",
            )

        item_in_history = filtered_comments_history_item.objects.get(id=1)

        self.assertIsNotNone(item_in_history)
    

class transferred_playlists_history_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )
        user_data_storage.objects.create(user=User.objects.get(username="testUser"))

    def test_transferred_playlists_history(self):
        """Saving transferred playlists works correctly"""
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUser"))
        
        if storage.save_history:
            transferred_playlists_history_item.objects.create(
                user = User.objects.get(username="testUser"),
                title = "Example Of Youtube Video Title",
                link = "https://www.youtube.com",
            )

        item_in_history = transferred_playlists_history_item.objects.get(id=1)

        self.assertIsNotNone(item_in_history)  


class Ticket_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

    def test_tickets(self):
        """Tickets work correctly"""
        
        Ticket.objects.create(
            user = User.objects.get(username="testUser")
        )

        ticket = Ticket.objects.get(id=1)
        self.assertEqual(ticket.remaining_tickets, 3)  

        ticket.remaining_tickets -= 1
        self.assertEqual(ticket.remaining_tickets, 2)


        reset_time = timezone.now().astimezone() + datetime.timedelta(hours=24) 

        if reset_time > ticket.last_reset_time:
            ticket.remaining_tickets = 3
            ticket.last_reset_time = reset_time.replace(hour=0, minute=0, second=0, microsecond=0)
            ticket.save()

        self.assertEqual(ticket.remaining_tickets, 3)


class UpdateUserForm_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

    def test_UpdateUserForm(self):
        """Updating Form works correctly"""
        user = User.objects.get(username="testUser")
        user_data_storage.objects.create(user=user)

        form = UpdateUserForm(
            {
            "username":"testUserUpdated",
            "email" : "test@testUpdated.com",
            "save_history": False,
            }
        , instance=user)

        self.assertEqual(form.is_valid(), True)
        
        form.save()
        storage = user_data_storage.objects.get(user=User.objects.get(username="testUserUpdated"))


        self.assertEqual(user.username, "testUserUpdated")
        self.assertEqual(user.email, "test@testupdated.com") # Email to lowercase
        self.assertEqual(storage.save_history, False)



"""
Api endpoints

"""



class RetrieveDownloadHistory_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

        Token.objects.create(user=User.objects.get(username="testUser"))


    def test_download_history_endpoint(self):
        user = User.objects.get(username='testUser')
        token = Token.objects.get(user=user)

        request = self.client.get(
            '/api/download_history/', 
            format='json',
            **{'HTTP_AUTHORIZATION': f'Token {token}'},
            )

        self.assertEqual(request.status_code, status.HTTP_200_OK)


class RetrievePromptsHistory_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

        Token.objects.create(user=User.objects.get(username="testUser"))


    def test_prompts_history_endpoint(self):
        user = User.objects.get(username='testUser')
        token = Token.objects.get(user=user)

        request = self.client.get(
            '/api/prompts_history/', 
            format='json',
            **{'HTTP_AUTHORIZATION': f'Token {token}'},
            )

        self.assertEqual(request.status_code, status.HTTP_200_OK)


class RetrieveFilteredCommentsHistory_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

        Token.objects.create(user=User.objects.get(username="testUser"))


    def test_filtered_comments_history_endpoint(self):
        user = User.objects.get(username='testUser')
        token = Token.objects.get(user=user)

        request = self.client.get(
            '/api/filtered_comments_history/', 
            format='json',
            **{'HTTP_AUTHORIZATION': f'Token {token}'},
            )

        self.assertEqual(request.status_code, status.HTTP_200_OK)


class RetrieveTransferredPlaylistsHistory_Test(TestCase):
    def setUp(self):
        User.objects.create(
            username="testUser",
            email="test@test.com",
            password="test"
        )

        Token.objects.create(user=User.objects.get(username="testUser"))


    def test_transferred_playlists_history_endpoint(self):
        user = User.objects.get(username='testUser')
        token = Token.objects.get(user=user)

        request = self.client.get(
            '/api/transferred_playlists_history/', 
            format='json',
            **{'HTTP_AUTHORIZATION': f'Token {token}'},
            )

        self.assertEqual(request.status_code, status.HTTP_200_OK)
