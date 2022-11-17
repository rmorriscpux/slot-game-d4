# TODO: Remove custom elid_page_display function and use the function built into the Paginator object.

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from .models import User, GamesPlayed, Jackpot
from .slot import Slot
from .page_display import elid_page_display
import bcrypt

# index
# Path: /
# Main register/login page.
def index(request):
    if 'user_id' in request.session:
        current_user = User.objects.get(id=request.session['user_id'])
        messages.warning(request, f'Already logged in as {current_user.username}.')
    return render(request, "index.html")

# register
# Path: /register/
# Register a new user.
def register(request):
    if request.method == "POST":
        # Validate form data.
        errors = User.objects.reg_validation(request.POST)
        if errors:
            for msg in errors.values():
                messages.error(request, msg)
            return redirect("/")

        # No errors, create new user.
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            username = request.POST['username'],
            email = request.POST['email'],
            pw_hash = bcrypt.hashpw(request.POST['pw'].encode(), bcrypt.gensalt()).decode(),
            birthday = request.POST['dob'] # Model converts to date object.
        )

        # Start session and finish up.
        request.session.flush()
        request.session['user_id'] = new_user.id
        messages.success(request, "Registration successful!")
        return redirect("/user/")

    else: # Got here by some other means. Go to reg/login page.
        return redirect("/")

# login
# Path: /login/
# Log in and go to user page if successful, otherwise return to reg/login page.
def login(request):
    if request.method == "POST":
        request.session.flush()
        # Get user. Go back to login page if not found.
        find_user = User.objects.filter(username=request.POST['username'])
        if not find_user:
            messages.error(request, "Invalid credentials.")
            request.session.flush()
            return redirect("/")
        
        current_user = find_user[0]
        # Check the password.
        if bcrypt.checkpw(request.POST['pw'].encode(), find_user[0].pw_hash.encode()):
            request.session['user_id'] = find_user[0].id
            messages.success(request, "Login successful!")
            return redirect("/user/")
        else: # Invalid password.
            messages.error(request, "Invalid credentials.")
            request.session.flush()
            return redirect("/")

    else:
        return redirect("/")

# logout
# Path: /logout/
# Log out and go to main reg/login page.
def logout(request):
    request.session.flush()
    messages.success(request, "Logout successful.")
    return redirect("/")

# game_page
# Path: /game/
# Go to the game page if logged in. Give it the last game results if they exist.
def game_page(request):
    # Session check
    if 'user_id' not in request.session:
        return redirect("/")

    context = {}
    # Get game result dict object if exists. This comes redirected from game_play or persistence in the session.
    if 'game_result' in request.session:
        context['game_result'] = request.session['game_result']
    else: # Populate with default values.
        dummy_game = Slot()
        context['game_result'] = {
            'window' : dummy_game.window,
            'lines_played' : 1,
            'credits_won' : 0,
            'win_lines' : {},
        }
    context['current_user'] = User.objects.get(id=request.session['user_id'])
    
    return render(request, "game.html", context)

# game_spin
# Path: /game/spin/
# Play a game if the amount of credits bet is available.
def game_spin(request):
    # Session check
    if 'user_id' not in request.session:
        return redirect("/")

    if request.method == "POST":
        current_user = User.objects.get(id=request.session['user_id'])
        bet = int(request.POST['bet'])
        # Ensure that the player has enough credits.
        if current_user.credit_balance < bet:
            messages.error(request, "Insufficient credits.")
            return redirect("/game/")

        # Remove bet amount from player credits.
        initial_credits = current_user.credit_balance # Save for later.
        current_user.credit_balance -= bet
        # Play the game with the selected line bet.
        game_play = Slot().play(bet)
        if settings.DEBUG:
            game_play.print_window()
        # Update player stats.
        current_user.games_played += 1
        current_user.credits_played += game_play.game_result['credits_played']
        current_user.credits_won += game_play.game_result['credits_won']
        current_user.credit_balance += game_play.game_result['credits_won']
        current_user.save()
        # Add the top award to the jackpot list if hit.
        if game_play.game_result['top_award']:
            Jackpot.objects.create(awarded_to=current_user)
        # Add game history saving logic here. 
        user_games = current_user.last_games_played.order_by('created_at')
        # Remove the earliest games from the queue until the total is less than 10.
        for i in range(len(user_games), 9, -1):
            user_games.first().delete()
        # Add the new game to history.
        history_game = GamesPlayed.objects.create(
            credits_at_start = initial_credits,
            credits_at_end = current_user.credit_balance,
            credits_played = game_play.game_result['credits_played'],
            credits_won = game_play.game_result['credits_won'],
            reelstops = game_play.game_result['reelstops'],
            played_by = current_user,
        )

        request.session['game_result'] = {
            'window' : game_play.window,
            'lines_played' : game_play.game_result['credits_played'],
            'credits_won' : game_play.game_result['credits_won'],
            'win_lines' : game_play.game_result['wins'],
        }

    return redirect("/game/")

# user_info
# Path: /user/
# Direct logged in user to their user page.
def user_info(request):
    # Session Check
    if 'user_id' not in request.session:
        return redirect("/")

    # Get user data.
    current_user = User.objects.get(id=request.session['user_id'])
    context = {
        'username' : current_user.username,
        'user_first_name' : current_user.first_name,
        'user_last_name' : current_user.last_name,
        'user_email' : current_user.email,
        'user_credit_balance' : current_user.credit_balance,
        'user_games_played' : current_user.games_played,
        'user_credits_played' : current_user.credits_played,
        'user_credits_won' : current_user.credits_won,
    }
    
    return render(request, "user.html", context)

# show_history
# Path: /user/history/?record=<int>
# Get a game history record and siaplay it.
def show_history(request):
    # Session check
    if 'user_id' not in request.session:
        return redirect('/')

    # Set vars needed.
    current_user = User.objects.get(id=request.session['user_id'])
    game_records = current_user.last_games_played.all().order_by('created_at')
    game_record_count = len(game_records)

    # Case: game_records is empty (user has not played games yet)
    # Go to history.html page and do the logic there showing that there is no game history.
    context = {}
    if game_record_count == 0:
        context['current_user'] = current_user
        context['record_count'] = game_record_count
        return render(request, "history.html", context)

    # Take the specific record, with some input handling. Important since we're using GET data.
    if 'record' not in request.GET:
        record_index = game_record_count - 1
    elif not request.GET['record'].isnumeric(): # Seems a bit verbose, but it looks safer.
        record_index = game_record_count - 1
    else:
        record_index = int(request.GET['record'])

    # Boundary check.
    if record_index < 0:
        record_index = 0
    elif record_index >= game_record_count:
        record_index = game_record_count - 1

    # Rebuild game.
    game_data = game_records[record_index]
    game_recall = Slot(game_data.reelstops[0], game_data.reelstops[1], game_data.reelstops[2])
    game_recall.eval_lines(game_data.credits_played)

    # Now to put together everything needed for the template.
    context['current_user'] = current_user
    context['game_result'] = {
        'window' : game_recall.window,
        'lines_played' : game_data.credits_played,
        'credits_won' : game_data.credits_won,
        'credits_at_start' : game_data.credits_at_start,
        'credits_at_end' : game_data.credits_at_end,
        'win_lines' : game_recall.game_result['wins'],
    }
    context['timestamp'] = game_data.created_at.strftime("%b %d %Y, %I:%M:%S %p")
    # Needed to determine arrows.
    context['record_index'] = record_index
    context['record_count'] = game_record_count

    return render(request, "history.html", context)

# add_credit
# Path: /user/add_credit/
# Add credits to a user account.
def add_credit(request):
    # Session Check
    if 'user_id' not in request.session:
        return redirect("/")

    if request.method == "POST":
        to_add = int(request.POST['amount'])
        if to_add > 0 and to_add <= 100:
            current_user = User.objects.get(id=request.session['user_id'])
            current_user.credit_balance += to_add
            current_user.save()
            messages.success(request, "Credits added successfully!")
        else:
            messages.error(request, "Invalid credit amount. Must be between 1 and 100.")
    return redirect("/user/")

# confirm_delete
# Path: /user/confirm_delete/
# Go to page to confirm deleting a user account.
def confirm_delete(request):
    # Session Check
    if 'user_id' not in request.session:
        return redirect("/")

    context = {}
    context['current_user'] = User.objects.get(id=request.session['user_id'])
    return render(request, 'delete_confirm.html', context)

# destroy_user
# Path: /user/destroy/
# Delete a user after confirmation.
def destroy_user(request):
    # Session Check
    if 'user_id' not in request.session:
        return redirect("/")

    if request.method == "POST":
        current_user = User.objects.get(id=request.session['user_id'])

        # Password check.
        if bcrypt.checkpw(request.POST['pw'].encode(), current_user.pw_hash.encode()):
            # Password good. Proceed with destroying user account.
            current_user.delete()
            request.session.flush()
            messages.success(request, "Account deleted successfully.")
            return redirect('/')
        else:
            # Invalid password.
            messages.error(request, "Invalid password.")
            return redirect('/user/confirm_delete/')
    
    else:
        # Did not get here from the form.
        return redirect('/user/')

# jackpot_list
# Path: /jackpots/
# Render list of jackpots. Users can give kudos.
def jackpot_list(request):
    # Session check
    if 'user_id' not in request.session:
        return redirect('/')

    context = {}
    # Get the jackpots, latest hits first, 10 per page.
    # Maybe set an upper limit on total jackpots available to display?
    jackpot_pages = Paginator(Jackpot.objects.all().order_by('-created_at'), 10)

    # Determine which page to display. This will be from a GET value normally.
    if 'page' not in request.GET:
        display_page = 1
    elif not request.GET['page'].isnumeric(): # Seems a bit verbose, but it looks safer.
        display_page = 1
    elif int(request.GET['page']) not in jackpot_pages.page_range: # Check that the page number is valid. If not, default to 1.
        display_page = 1
    else: # We have a valid page number in request.GET['page'].
        display_page = int(request.GET['page'])

    # Now set the objects to send.
    context['display_jackpots'] = jackpot_pages.get_page(display_page)

    context['current_page'] = display_page
    context['page_range'] = elid_page_display(jackpot_pages.page_range, display_page, 1, 2)
    context['current_user'] = User.objects.get(id=request.session['user_id'])
    context['num_pages'] = jackpot_pages.num_pages

    return render(request, "jackpot_list.html", context)

# kudos
# Path: /jackpots/kudos/<int:jackpot_id>/
# Give kudos to a jackpot win.
def kudos(request, jackpot_id):
    # Session check
    if 'user_id' not in request.session:
        return redirect('/')

    if request.method == "POST":
        jp = Jackpot.objects.get(id=jackpot_id)
        current_user = User.objects.get(id=request.session['user_id'])

        if current_user not in jp.liked_by.all() and current_user != jp.awarded_to:
            jp.liked_by.add(current_user)

        return redirect(f"/jackpots/?page={request.POST['redirect_page']}")

    else:
        return redirect("/jackpots/")

# undo_kudos
# Path: /jackpots/undo_kudos/<int:jackpot_id>/
# Give kudos to a jackpot win.
def undo_kudos(request, jackpot_id):
    # Session check
    if 'user_id' not in request.session:
        return redirect('/')

    if request.method == "POST":
        jp = Jackpot.objects.get(id=jackpot_id)
        current_user = User.objects.get(id=request.session['user_id'])

        if current_user in jp.liked_by.all():
            jp.liked_by.remove(current_user)

        return redirect(f"/jackpots/?page={request.POST['redirect_page']}")

    else:
        return redirect("/jackpots/")

if settings.DEBUG:
    # test_page
    # Path: /test/
    def test_page(request):
        my_game = Slot().play(5).print_window()
        print("Played: " + str(my_game.game_result['credits_played']))
        print("   Won: " + str(my_game.game_result['credits_won']))
        for line, win in my_game.game_result['wins'].items():
            print(line + " pays " + str(win))
        context = {
            'window' : my_game.window,
            'played' : my_game.game_result['credits_played'],
            'total_won' : my_game.game_result['credits_won'],
            'wins' : my_game.game_result['wins'],
            'symbol' : "Banana"
        }
        return render(request, "test_page.html", context)