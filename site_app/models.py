from django.db import models
from datetime import date
import re

class UserMgr(models.Manager):
    # Validate the data entered on a registration.
    def reg_validation(self, post_data):
        NAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z]+$')
        USERNAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9]{4,}$')
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        # Check first name
        if not NAME_REGEX.match(post_data['first_name']):
            errors['first_name'] = "First name must be at least 2 alphabetical characters."
        # Check last name
        if not NAME_REGEX.match(post_data['last_name']):
            errors['last_name'] = "Last name must be at least 2 alphabetical characters."
        # Check username
        if not USERNAME_REGEX.match(post_data['username']):
            errors['username'] = "Invalid username. Must start with a letter and be 5 alphanumeric characters long."
        existing_user = self.filter(username=post_data['username'])
        if existing_user: # Username found.
            errors['username'] = "Username already exists."
        # Check email
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Invalid email address."
        existing_email = self.filter(email=post_data['email'])
        if existing_email:
            errors['email'] = "Email address already exists."
        # Check Password (There has to be a better way to do this)
        if (re.search("[a-z]", post_data['pw']) == None or
            re.search("[A-Z]", post_data['pw']) == None or
            re.search("[0-9]", post_data['pw']) == None or
            re.search("[^a-zA-Z0-9]", post_data['pw']) == None or
            len(post_data['pw']) < 8):
            errors['password'] = "Password must be at least 8 characters and contain at least 1 capital letter, 1 lowercase letter, 1 number, and 1 special character."
        elif post_data['pw'] != post_data['confirm_pw']:
            errors['password'] = "Passwords do not match."
        # Check Birthday
        try:
            # entered_birthday = date.fromisoformat(post_date['dob'])
            # Python version < 3.7 compatible.
            date_arr = post_data['dob'].split('-')
            entered_birthday = date(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))
        except:
            errors['dob'] = "Invalid date of birth."
        else:
            if entered_birthday > date.today().replace(year=date.today().year-21):
                errors['dob'] = "Must be at least 21 years of age to register."

        return errors

class User(models.Model):
    # Unique Fields
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    username = models.CharField(max_length=45)
    email = models.CharField(max_length=255)
    pw_hash = models.CharField(max_length=255)
    birthday = models.DateField()
    credit_balance = models.PositiveIntegerField(default=0)
    games_played = models.PositiveIntegerField(default=0)
    credits_played = models.PositiveIntegerField(default=0)
    credits_won = models.PositiveIntegerField(default=0)

    # Relationships
    # last_games_played: GamesPlayed objects
    # jackpots: Jackpot objects
    # jackpot_kudos: Jackpot many-to-many

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    objects = UserMgr()

class GamesPlayed(models.Model):
    # Unique Fields
    credits_at_start = models.PositiveIntegerField()
    credits_at_end = models.PositiveIntegerField()
    credits_played = models.PositiveIntegerField()
    credits_won = models.PositiveIntegerField()
    _reelstop_blob = models.PositiveIntegerField(default=0, db_column="reelstops")

    @property
    def reelstops(self):
        # Get 3 reel stops from the _reelstop_blob value.
        stops = []
        blob_parser = self._reelstop_blob
        stops.insert(0, blob_parser % 256)
        blob_parser >>= 8
        stops.insert(0, blob_parser % 256)
        blob_parser >>= 8
        stops.insert(0, blob_parser % 256)
        return stops

    @reelstops.setter
    def reelstops(self, stops):
        # Validate input.
        input_validator = isinstance(stops, list) # Check that it's a list.
        if input_validator:
            input_validator = len(stops) == 3 # Check that the list length is 3.
        if input_validator:
            input_validator = all(list(map(lambda num: isinstance(num, int), stops))) # Check that each item in the list is an integer.
        if input_validator:
            input_validator = all(list(map(lambda num: num < 256 and num >= 0, stops))) # Check that each iterm in the list is between 0 and 255.
        # When all is good, set the blob.
        if input_validator:
            self._reelstop_blob = 0
            self._reelstop_blob += stops[0] << 16
            self._reelstop_blob += stops[1] << 8
            self._reelstop_blob += stops[2]

    # Relationships
    played_by = models.ForeignKey(User, related_name="last_games_played", on_delete=models.CASCADE)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Jackpot(models.Model):
    # Unique Fields

    # Relationships
    awarded_to = models.ForeignKey(User, related_name="jackpots", on_delete=models.CASCADE) # Note: in a real site, user accounts would be deactivated instead of outright deleted.
    liked_by = models.ManyToManyField(User, related_name="jackpot_kudos")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)