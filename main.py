import discord
from discord import Intents
import random
import asyncio

intents = Intents.default()
intents.message_content = True  # Enable receiving message content
client = discord.Client(intents=intents)

registration_channel_id = 1265820482259783814
balance_channel_id = 1265488531371851786
game_channel_id = 1265485664653410374  # Channel where game commands are allowed
accounts = {}

# Define the channel IDs for each command
spin_channel_id = 1266457328388018278
crash_channel_id = 1266457142156726345
cube_channel_id = 1266457436290682961
blackjack_channel_id = 1266457596492120175
dice_channel_id = 1266457742516682855

@client.event
async def on_ready():
    global registration_channel, balance_channel, game_channel
    registration_channel = client.get_channel(registration_channel_id)
    balance_channel = client.get_channel(balance_channel_id)
    game_channel = client.get_channel(game_channel_id)
    print(f'Logged in as {client.user}')
    print(f'Registration channel: {registration_channel}')
    print(f'Balance channel: {balance_channel}')
    print(f'Game channel: {game_channel}')
    await load_accounts()  # Load existing accounts from the registration channel

async def load_accounts():
    global accounts
    if registration_channel is None:
        print('Registration channel not found.')
        return

    accounts = {}
    async for message in registration_channel.history(limit=100):
        if message.author == client.user:
            if message.content.startswith('Account created for'):
                parts = message.content.split()
                user_id = parts[3][2:-1]  # Extract user ID from <@123456789012345678>
                accounts[user_id] = None  # Initial placeholder for balance

    print('Accounts loaded:', accounts)
    await update_balances()

async def update_balances():
    if balance_channel is None:
        print('Balance channel not found.')
        return

    async for message in balance_channel.history(limit=100):
        if message.content.startswith('<@'):
            parts = message.content.split()
            user_id = parts[0][2:-1]  # Extract user ID from <@123456789012345678>
            balance = float(parts[-1].replace('$', ''))
            if user_id in accounts:
                accounts[user_id] = balance

    print('Balances updated:', accounts)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!c-account'):
        await handle_create_account_command(message)
    elif message.content.startswith('!casino'):
        await handle_casino_command(message)
    elif message.content.startswith('!spin'):
        if message.channel.id == spin_channel_id:
            await handle_spin_command(message)
    elif message.content.startswith('!cube'):
        if message.channel.id == cube_channel_id:
            await handle_cube_command(message)
    elif message.content.startswith('!crash'):
        if message.channel.id == crash_channel_id:
            await handle_crash_command(message)
    elif message.content.startswith('!blackjack'):
        if message.channel.id == blackjack_channel_id:
            await handle_blackjack_command(message)
    elif message.content.startswith('!dice'):
        if message.channel.id == dice_channel_id:
            await handle_dice_command(message)
    elif message.content.startswith('!add'):
        await handle_add_command(message)

async def handle_create_account_command(message):
    user_id = str(message.author.id)

    if user_id in accounts and accounts[user_id] is not None:
        await message.channel.send('⛳︱You already have an account.')
        return

    accounts[user_id] = 1000.0
    if registration_channel is not None:
        await registration_channel.send(f'Account created for {message.author} with balance $1000.0')
    if balance_channel is not None:
        await balance_channel.send(f'{message.author} balance: $1000.0')
    await message.channel.send(f'💳︱**Account created!** You have earned the starting balance of **$1000.0**')

async def handle_casino_command(message):
    user_id = str(message.author.id)

    # Check if account exists in registration channel
    account_found = False
    if registration_channel is not None:
        async for msg in registration_channel.history(limit=100):
            if msg.content.startswith(f'Account created for {message.author}'):
                account_found = True
                break

    if not account_found:
        await message.channel.send('⛳︱**No account found**. Please create an account using !c-account.')
        return

    # Retrieve latest balance from balance channel
    balance = 0
    if balance_channel is not None:
        async for msg in balance_channel.history(limit=100):
            if msg.content.startswith(f'{message.author} balance:'):
                parts = msg.content.split()
                balance = float(parts[-1].replace('$', ''))
                break

    accounts[user_id] = balance
    await message.channel.send(f'🎰︱**Welcome** back to **EARTH** Server Casino! 💵︱Your current balance is ${balance:.2f}. **Start the game ** that  **matches the channel **. If you have any doubts about the commands, go to the guide on the channel 🎰︱𝗖𝗔𝗦𝗜𝗡𝗢')

# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉
    async def handle_spin_command(message):
        user_id = str(message.author.id)
        if user_id not in accounts or accounts[user_id] is None:
            await message.channel.send('⛳︱**Check if there is an account** created using `!casino`, if not **You need to create an account** first using `!c-account`')
            return

        balance = accounts[user_id]
        await message.channel.send(f'💵︱**Your current balance** is ${balance:.2f}. 💳︱How much do you **want to bet?**')

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.isdigit()

        bet_msg = await client.wait_for('message', check=check)
        bet = int(bet_msg.content)

        if bet > balance:
            await message.channel.send('⛳︱**You do not have enough** balance to place this bet.')
            return

        accounts[user_id] -= bet
        await show_balance(message.author)
        await message.channel.send('🎰︱It’s **spinning!** [5 seconds]')

        await asyncio.sleep(2.5)
        emojis = ["🍎", "💵", "💸", "🍎", "🍒", "🎸"]
        result = [random.choice(emojis) for _ in range(3)]
        result_str = ' '.join(result)
        await message.channel.send(result_str)

        if result[0] == result[1] == result[2]:
            winnings = bet * 2
            accounts[user_id] += winnings
            await message.channel.send(f'🎉︱**You won!** Your new balance is ${accounts[user_id]:.2f}')
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            winnings = 100.0
            accounts[user_id] += winnings
            await message.channel.send(f'🎉︱**You got two images the same!** You won ${winnings:.2f}. Your new balance is ${accounts[user_id]:.2f}')
        else:
            await message.channel.send('🧩︱**You lost!** Try other games or try your luck again')

        await show_balance(message.author)

# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉

async def handle_cube_command(message):
    user_id = str(message.author.id)
    if user_id not in accounts or accounts[user_id] is None:
        await message.channel.send('🌴︱**You need to create an account** first using !c-account')
        return

    balance = accounts[user_id]
    await message.channel.send(f'💳︱**Your current balance** is ${balance:.2f}. 💸︱How much do you **want to bet?**')

    def check(m):
        return m.author == message.author and m.channel == message.channel and m.content.isdigit()

    bet_msg = await client.wait_for('message', check=check)
    bet = int(bet_msg.content)

    if bet > balance:
        await message.channel.send('🧩︱**You do not have enough** balance to place this bet.')
        return

    await message.channel.send('🎲︱**Pick 3 numbers** from **1 to 6 separated by spaces.**')

    def check_number(m):
        return m.author == message.author and m.channel == message.channel and all(i.isdigit() and 1 <= int(i) <= 6 for i in m.content.split())

    numbers_msg = await client.wait_for('message', check=check_number)
    numbers = list(map(int, numbers_msg.content.split()))

    if len(numbers) != 3:
        await message.channel.send('⛳︱**You must pick exactly 3 numbers.**')
        return

    dice_results = [random.randint(1, 6) for _ in range(3)]
    dice_results_str = ' '.join(map(str, dice_results))
    await message.channel.send(f'🎲︱Dice results: {dice_results_str}')

    if sorted(numbers) == sorted(dice_results):
        winnings = bet * 10
        accounts[user_id] += winnings
        await message.channel.send(f'🎉︱**Congratulations!** You won ${winnings:.2f}. Your new balance is ${accounts[user_id]:.2f}')
    else:
        await message.channel.send('🧩︱**Sorry, you lost this time.** Try again!')

    await show_balance(message.author)

# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉
async def handle_crash_command(message):
        user_id = str(message.author.id)
        if user_id not in accounts or accounts[user_id] is None:
            await message.channel.send('🌴︱**You need to create an account** first using !c-account')
            return

        balance = accounts[user_id]
        await message.channel.send(f'💳︱**Your current balance** is ${balance:.2f}. ⛳︱How much do you **want to bet?**')

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.isdigit()

        bet_msg = await client.wait_for('message', check=check)
        bet = int(bet_msg.content)

        if bet > balance:
            await message.channel.send('🌴︱**You do not have enough** balance to place this bet.')
            return

        accounts[user_id] -= bet
        await show_balance(message.author)
        await message.channel.send('📈︱**Every second**, the amount you bet will be **multiplied**. Use !stop before the chart crashes. 🧨︱Send `!startcrash` to start.')

        def check_start(m):
            return m.author == message.author and m.channel == message.channel and m.content == '!startcrash'

        await client.wait_for('message', check=check_start)
        await message.channel.send('📈︱Multiplication **started** ︱ Use `!stop` before the chart crashes')

        stop_received = False

        def check_stop(m):
            nonlocal stop_received
            if m.author == message.author and m.channel == message.channel and m.content == '!stop':
                stop_received = True
                return True
            return False

        random_crash_time = random.uniform(1, 10)  # Random time between 1 and 10 seconds
        start_time = asyncio.get_event_loop().time()

        while True:
            try:
                await asyncio.wait_for(client.wait_for('message', check=check_stop), timeout=1)
            except asyncio.TimeoutError:
                elapsed_time = asyncio.get_event_loop().time() - start_time
                multiplier = 0.5 * elapsed_time  # 0.5x per second

                if elapsed_time >= random_crash_time:
                    break

            if stop_received:
                break

        if stop_received:
            winnings = bet * multiplier
            accounts[user_id] += winnings
            await message.channel.send(f'💼︱**Stop received!** You won ${winnings:.2f}.')
        else:
            await message.channel.send('🧨💥︱**Multiplication CRASHED**, you lost everything! Try again')

        await show_balance(message.author)

async def show_balance(user):
        if balance_channel is not None:
            balance = accounts.get(str(user.id), 0)
            await balance_channel.send(f'{user} balance: ${balance:.2f}')

# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉
async def handle_dice_command(message):
    if message.channel.id != dice_channel_id:
        return

    user_id = str(message.author.id)
    if user_id not in accounts or accounts[user_id] is None:
        await message.channel.send('🌴︱**You need to create an account** first using !c-account')
        return

    balance = accounts[user_id]
    await message.channel.send(f'💳︱**Your current balance** is ${balance:.2f}. ⛳︱How much do you **want to bet?**')

    def check(m):
        return m.author == message.author and m.channel == message.channel and m.content.isdigit()

    bet_msg = await client.wait_for('message', check=check)
    bet = int(bet_msg.content)

    if bet > balance:
        await message.channel.send('🌴︱**You do not have enough** balance to place this bet.')
        return

    accounts[user_id] -= bet
    await show_balance(message.author)

    await message.channel.send('🎲︱**Guess the sum** of two dice rolls (between 2 and 12):')

    def check_guess(m):
        return m.author == message.author and m.channel == message.channel and m.content.isdigit() and 2 <= int(m.content) <= 12

    guess_msg = await client.wait_for('message', check=check_guess)
    guess = int(guess_msg.content)

    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2

    await message.channel.send(f'🎲︱**The dice rolled:** {dice1} and {dice2} (Total: {total})')

    if guess == total:
        winnings = 500.0
        accounts[user_id] += winnings
        await message.channel.send(f'🎉︱**Congratulations!** You guessed correctly and won ${winnings:.2f}. Your new balance is ${accounts[user_id]:.2f}')
    else:
        await message.channel.send(f'💥︱**Sorry, you guessed wrong.** Try again next time!')

    await show_balance(message.author)
# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉

async def handle_blackjack_command(message):
    if message.channel.id != 1266457596492120175:
        return

    user_id = str(message.author.id)
    if user_id not in accounts or accounts[user_id] is None:
        await message.channel.send('🌴︱**You need to create an account** first using !c-account')
        return

    balance = accounts[user_id]
    await message.channel.send(f'💳︱**Your current balance** is ${balance:.2f}. ⛳︱How much do you **want to bet?**')

    def check(m):
        return m.author == message.author and m.channel == message.channel and m.content.isdigit()

    bet_msg = await client.wait_for('message', check=check)
    bet = int(bet_msg.content)

    if bet > balance:
        await message.channel.send('🌴︱**You do not have enough** balance to place this bet.')
        return

    accounts[user_id] -= bet
    await show_balance(message.author)

    deck = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] * 4
    random.shuffle(deck)

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    await message.channel.send(f'🃏︱**Your hand**: {player_hand} (Value: {calculate_hand_value(player_hand)})')
    await message.channel.send(f'🃏︱**Dealer\'s hand**: [{dealer_hand[0]}, ?]')

    while calculate_hand_value(player_hand) < 21:
        await message.channel.send('💳︱**Hit or stand? (h/s)**')

        def check_hs(m):
            return m.author == message.author and m.channel == message.channel and m.content.lower() in ["h", "s"]

        hs_msg = await client.wait_for('message', check=check_hs)
        if hs_msg.content.lower() == "h":
            player_hand.append(deck.pop())
            await message.channel.send(f'🃏︱**Your hand**: {player_hand} (Value: {calculate_hand_value(player_hand)})')
        else:
            break

    player_value = calculate_hand_value(player_hand)
    if player_value > 21:
        await message.channel.send('💥︱**Bust! You lose.**')
    else:
        await message.channel.send(f'🃏︱**Dealer\'s hand**: {dealer_hand} (Value: {calculate_hand_value(dealer_hand)})')
        while calculate_hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
            await message.channel.send(f'🃏︱**Dealer\'s hand**: {dealer_hand} (Value: {calculate_hand_value(dealer_hand)})')

        dealer_value = calculate_hand_value(dealer_hand)
        if dealer_value > 21 or player_value > dealer_value:
            winnings = bet * 2
            accounts[user_id] += winnings
            await message.channel.send(f'🎉︱**You win!** Your new balance is ${accounts[user_id]:.2f}')
        elif player_value == dealer_value:
            accounts[user_id] += bet
            await message.channel.send('🔄︱**Push! It\'s a tie.**')
        else:
            await message.channel.send('💥︱**Dealer wins!**')
      
    await show_balance(message.author)

def calculate_hand_value(hand):
    value = 0
    num_aces = hand.count("A")
    for card in hand:
        if card in ["J", "Q", "K"]:
            value += 10
        elif card == "A":
            value += 11
        else:
            value += int(card)
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

# ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉

client.run(process.env.TOKEN);
