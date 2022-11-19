from mcapi import *
# from python.mcapi import *

# from org.bukkit.event.player import PlayerJoinEvent
# from org.bukkit.inventory import ItemStack
# from org.bukkit import ChatColor, Material
# import urllib2
# import json

# from org.bukkit.event.player import PlayerJoinEvent
from org.bukkit.inventory import ItemStack
from org.bukkit import ChatColor, Material
import urllib2
import json
import random
from datetime import date
import math

""" Helper functions """

# TODO => How wide is the chat window? 47 characters => prob. 48 | 58?
# NOPE:: 57!!

def colored_text(text, color):
    colors = color if isinstance(color, list) else [ color ]
    return ("{}" * len(colors)).format(*colors) + "{}{}".format(text, ChatColor.RESET)

def pad_and_center_string(text, n_chars):
    text = str(text)
    pad = n_chars - len(text)
    padf = pad//2
    padb = pad - padf
    return "{}{}{}".format(" "*padf, text, " "*padb) 

def pad_string_left(text, n_chars):
    text = str(text)
    npad = n_chars - len(text)
    return " "*npad + text

def pad_string_right(text, n_chars):
    text = str(text)
    npad = n_chars - len(text)
    return text + npad * " "


def get_column_sizes(data):
    col_sz = None
    for row in data:
        if col_sz is None:
            col_sz = [ len(str(e)) for e in row ]
        else:
            col_sz = [ max(len(str(e)), col_sz[i]) for i, e in enumerate(row) ]

    return col_sz

def print_exchange_help(player_name, display_title=True):
    p = player(player_name)
    if display_title:
        p.sendMessage(
            "{}{}{}".format(
                colored_text('#', ChatColor.MAGIC),
                colored_text(pad_and_center_string("Welcome to McExchange", 55), [ ChatColor.YELLOW, ChatColor.BOLD ]),
                colored_text('#', ChatColor.MAGIC)
            )
        )
        p.sendMessage("Here you can sell and buy items from other players")
        p.sendMessage("Usage:")
    # SELL
    p.sendMessage("{} {} {} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("sell", [ ChatColor.YELLOW ]),
        colored_text("<price>", [ ChatColor.GREEN ]),
        colored_text("<amount, optional>", [ ChatColor.GREEN, ChatColor.ITALIC ]),
    ))
    # BUY
    p.sendMessage("{} {} {} {} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("buy", [ ChatColor.YELLOW ]),
        colored_text("<item name>", [ ChatColor.GREEN ]),
        colored_text("<price>", [ ChatColor.GREEN ]),
        colored_text("<amount>", [ ChatColor.GREEN ]),
    ))
    # BALANCE
    p.sendMessage("{} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("balance", [ ChatColor.YELLOW ]),
    ))
    # UPDATE
    p.sendMessage("{} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("update", [ ChatColor.YELLOW ]),
    ))
    # RETREIVE
    p.sendMessage("{} {} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("retreive", [ ChatColor.YELLOW ]),
        colored_text("<id>", [ ChatColor.GREEN ]),
    ))
    # ORDERBOOK
    p.sendMessage("{} {}".format(
        colored_text("/exchange", [ ChatColor.BOLD ]),
        colored_text("orders", [ ChatColor.YELLOW ]),
    ))


usernames = [
    'Intel4004',
    'Someone3lse',
    'Hackerman',
    'RonaldTheDuck'
]

item_names = [
    'Dirt',
    'Gold Block',
    'Hay Bale',
    'Chicken',
    'Nuggets'
]

order_display_header = ['Type', 'Name', 'Price', 'Issuer']
def random_order():
    type = 'BUY ' if random.random() > 0.5 else 'SELL'
    user_name = usernames[int(random.random() * len(usernames))]
    cost = int(400 + 1000 * random.random())
    item_name = item_names[int(random.random() * len(item_names))]
    return [ type, item_name, cost, user_name]




""" API Module """


def http_get(endpoint):
    req = urllib2.Request(endpoint)
    response = urllib2.urlopen(req)
    data = response.read()
    return data

def get_balance(player_name):
    response = http_get('http://demo1945772.mockable.io/balance')
    return json.loads(response)['balance']

all_orders = [ [ str(e) for e in random_order() ] for _ in range(100)]
def get_orders(search = None, page=0):
    filtered_orders = [ o for o in all_orders if search in o[1]] if search else all_orders
    n_pages = int(math.ceil(len(filtered_orders) / 8))
    current_page = min(page, n_pages)

    return current_page, n_pages, filtered_orders[page*8: (page+1)*8]

def get_updates(player_name):
    n_sold = 10
    sold_profit = 1000
    bought = [
        { "id": 0,  "name": 'Gold Block', "amount": 100 },
        { "id": 1, "name": 'Dirt', "amount": 1024 },
        { "id": 2, "name": 'Dirt', "amount": 1024 },
        { "id": 3, "name": 'Dirt', "amount": 1024 }
    ]
    return n_sold, sold_profit, bought

def retrieve_by_id(player_name, order_id):
    return { "id": order_id, "name": 'Dirt', "amount": 512, "retreived": False }



""" SubCommand handlers """

def handle_balance(player_name, args):
    # Get a reference to the player
    p = player(player_name)

    if len(args) > 0:
         # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for balance command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("balance", [ ChatColor.YELLOW ]),
        ))
        return

    # Request balance from the server
    balance = get_balance(player_name)
    
    # Display it to the user
    p.sendMessage(
        "{}{}{}".format(
            colored_text('#', ChatColor.MAGIC),
            colored_text(pad_and_center_string("McExchange Balance", 55), [ ChatColor.YELLOW, ChatColor.BOLD ]),
            colored_text('#', ChatColor.MAGIC)
        )
    )
    p.sendMessage(
        "{}{}".format(
            colored_text("You have", [ChatColor.BOLD ]),
            colored_text(pad_string_left("{} $".format(balance), 54 - len("You have")), [ ChatColor.GOLD, ChatColor.BOLD ]),
        )
    )


def handle_sell(player_name, args):
    # Get a reference to the player and their inventory
    # And the item they're currently holding
    p = player(player_name)
    inventory = p.getInventory()
    item_in_hand = inventory.getItemInMainHand()
    item_in_hand_meta = item_in_hand.getItemMeta()

    # If no arguments were provided, display command help
    if len(args) == 0 or len(args) > 2:
        # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for sell command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {} {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("sell", [ ChatColor.YELLOW ]),
            colored_text("<price>", [ ChatColor.GREEN ]),
            colored_text("<amount, optional>", [ ChatColor.GREEN, ChatColor.ITALIC ]),
        ))
        return

    # Check if the player is holding anything:
    amount_in_hand = item_in_hand.getAmount()
    if amount_in_hand == 0:
        p.sendMessage(
            colored_text("To sell an item, you need to hold it in your hand when running the command.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return
    

    # Time to get the arguments
    sell_price = int(args[0])
    sell_count = int(args[1]) if len(args) == 2 else None

    print(amount_in_hand, sell_count, args, item_in_hand.getType().getKey())

    # TODO we need to check if it's a custom item we're dealing with -> NBT tags, etc

    # Get the item's name, so we can display more info to the user
    item_name = '<ITEMNAME>'
    if item_in_hand_meta.hasDisplayName():
        item_name = item_in_hand_meta.getDisplayName()
    elif item_in_hand_meta.hasLocalizedName():
        item_name = item_in_hand_meta.getLocalizedName()
    else:
        item_name = " ".join([ part.capitalize() for part in str(item_in_hand.getType()).split('_')])
    
    # Check if the count is valid:
    if sell_count is None:
        sell_count = amount_in_hand
    if amount_in_hand < sell_count:
        p.sendMessage(
            colored_text("Can't sell {} of {}, you're only holding {}".format(sell_count, item_name, amount_in_hand), [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return
    

    # # Gather the data needed for the request
    material = item_in_hand.getType()

    print("Player {} wants to sell {}x{} for {} each.".format(player_name, sell_count, material, sell_price))

    # Send the request
    # TODO

    # If okay, removed the item.
    item_in_hand.setAmount(amount_in_hand - sell_count)
    inventory.setItemInMainHand(item_in_hand)

    # Notifiy the player if everything went well
    p.sendMessage(
        colored_text("Success", [ ChatColor.GREEN, ChatColor.BOLD ])
    )
    p.sendMessage(
        "Created order to sell {} {} for {} each.".format(
            colored_text(str(sell_count), [ ChatColor.YELLOW, ChatColor.BOLD ]),
            colored_text(item_name + "s" if sell_count > 1 else "",  [ ChatColor.YELLOW, ChatColor.BOLD ]),
            colored_text(str(sell_price) + " $", [ ChatColor.YELLOW, ChatColor.BOLD ]),
        )
    )


def handle_buy(player_name, args):
    p = player(player_name)

    # If no arguments were provided, display command help
    if len(args) != 3:
        # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for buy command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {} {} {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("buy", [ ChatColor.YELLOW ]),
            colored_text("<item name>", [ ChatColor.GREEN ]),
            colored_text("<price>", [ ChatColor.GREEN ]),
            colored_text("<amount>", [ ChatColor.GREEN ]),
        ))
        return


    # Time to get the arguments
    item_name = args[0]
    item_price = int(args[1])
    item_amount = int(args[2])

    print(item_name, item_price, item_amount)

    total_price = item_amount * item_price
    user_balance = get_balance(player_name)

    if user_balance < total_price:
        p.sendMessage(
            "{}{}{}{}".format(
                colored_text("Can't open a buy-order for {} x {} - the total cost would be ".format(item_amount, item_name), [ ChatColor.RED, ChatColor.ITALIC ]),
                colored_text("{} $".format(total_price), [ ChatColor.RED, ChatColor.ITALIC, ChatColor.BOLD ]),
                colored_text(" and you only have ", [ ChatColor.RED, ChatColor.ITALIC ]),
                colored_text("{} $".format(user_balance), [ ChatColor.RED, ChatColor.ITALIC, ChatColor.BOLD ])
            )
        )
        return

    # Send the request
    # TODO

    # Notifiy the player if everything went well
    p.sendMessage(
        colored_text("Success", [ ChatColor.GREEN, ChatColor.BOLD ])
    )
    p.sendMessage(
        "Created order to buy {} {} for {} each.".format(
            colored_text(str(item_amount), [ ChatColor.YELLOW, ChatColor.BOLD ]),
            colored_text(item_name + "s" if item_amount > 1 else "",  [ ChatColor.YELLOW, ChatColor.BOLD ]),
            colored_text(str(item_price) + " $", [ ChatColor.YELLOW, ChatColor.BOLD ]),
        )
    )


def handle_orderbook(player_name, args):
    p = player(player_name)

    # Theoretically this could accept a filter as well
    # And page #
    # But later.

    # If no arguments were provided, display command help
    if len(args) == 0 or len(args) > 2:
        # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for orders command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {} {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("orders", [ ChatColor.YELLOW ]),
            colored_text("<search-query>", [ ChatColor.GREEN ]),
            colored_text("<page, optional>", [ ChatColor.GREEN, ChatColor.ITALIC ]),
        ))
        return

    search = args[0]
    page = int(args[1]) - 1 if len(args) > 1 else 0
    page = max(page, 0)

    # Ask the server for the data
    page, total_pages, orders = get_orders(search, page)


    # Calculate column sizes
    column_sizes = get_column_sizes([order_display_header] + orders)
    print(column_sizes)

    separator = ' || '
    # Header
    p.sendMessage(
        separator.join([
            colored_text(pad_and_center_string(h, column_sizes[i]), [ ChatColor.BOLD ]) for i, h in enumerate(order_display_header)
        ])
    )
    # Data
    for order in orders:
        p.sendMessage(separator.join([
            pad_string_right(h, column_sizes[i]) for i, h in enumerate(order)
        ]))
    # Footer?
    page_string = "Page {}/{}".format(page + 1, total_pages + 1)
    p.sendMessage(
        "{}{}".format(
            page_string,
            colored_text(pad_string_left(date.today().strftime("%d/%m/%Y"), 57 - len(page_string)), [ ChatColor.BOLD ])
        )
    )


def handle_update(player_name, args):
    # Get a reference to the player
    p = player(player_name)

    if len(args) > 0:
         # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for update command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("update", [ ChatColor.YELLOW ]),
        ))
        return

    # Check if there's any updates for the user:
    n_sold, sell_profit, bought = get_updates(player_name)
    
    # Display it to the user
    p.sendMessage(
        "Over the last 24H, you have sold {} items, for a total profit of {}".format(
            n_sold,
            colored_text("{} $".format(sell_profit), [ ChatColor.GOLD ])
        )
    )
    p.sendMessage(
        "You also have {} item's you've bought but not yet collected:".format(len(bought))
    )

    p.sendMessage(
        "{} | {} | {}".format(
            colored_text(pad_and_center_string("ID", 20), [ ChatColor.BOLD ]),
            colored_text(pad_and_center_string("Name", 28), [ ChatColor.BOLD ]),
            colored_text(pad_and_center_string("Amount", 6), [ ChatColor.BOLD ]),
        )
    )
    for pending_item in bought:
        p.sendMessage(
        "{} | {} | {}".format(
            colored_text(pad_string_right(pending_item['id'], 20), [ ChatColor.BOLD ]),
            colored_text(pad_and_center_string(pending_item['name'], 28), [ ChatColor.BOLD ]),
            colored_text(pad_string_left(pending_item['amount'], 6), [ ChatColor.BOLD ]),
        )
    )


def handle_retreive(player_name, args):
    # Get a reference to the player
    p = player(player_name)

    if len(args) == 0 or len(args) > 1:
        # Display help
        p.sendMessage(
            colored_text("Incorrect amount of arguments for retrieve command", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        p.sendMessage("Usage: {} {} {} {}".format(
            colored_text("/exchange", [ ChatColor.BOLD ]),
            colored_text("retrieve", [ ChatColor.YELLOW ]),
            colored_text("<id>", [ ChatColor.GREEN ])
        ))
        return


    # Get the contents of the order
    order_id = args[0]
    data = retrieve_by_id(player_name, order_id)

    # Check if something was found
    if data is None or data['retreived']:
        p.sendMessage(
            colored_text("No unretreived order with the given id {} was found for user {}".format(order_id, player_name), [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return

    #  resolve the material:
    material_name = data['name'].replace(' ', '_').upper()
    material = Material.getMaterial(material_name)
    if material is None:
        p.sendMessage(
            colored_text("Cannot unpack order with id {} since we can't find the minecraft equivalent for {}".format(order_id, material_name), [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return

    # Check how many stacks we need to be empty:
    n_stacks = int(math.ceil(data['amount'] / 64))
    
    # Check if the player has enough free space in their inventory
    inventory_contents = p.getInventory().getContents()
    free_stack_indices = []
    for i, stack in enumerate(inventory_contents):
        # Ignore items with # > 35 -> armor slots etc
        if i < 36 and (stack is None or stack.getAmount() == 0) :
            free_stack_indices.append(i)

    if len(free_stack_indices) < n_stacks:
        p.sendMessage(
            colored_text(
                "The order occupies {} stacks, but you only have {} free - please make some more space in your inventory".format(
                    n_stacks,
                    len(free_stack_indices)
                )
            ,[ ChatColor.RED, ChatColor.ITALIC ])
        )
        return

    # begin unpacking!
    p.sendMessage(
        colored_text("Starting to unpack your order!", [ ChatColor.GREEN, ChatColor.BOLD ])
    )

    remaining_items = data['amount']
    while remaining_items > 0:
        stack_size = 64 if remaining_items > 64 else remaining_items
        stack = ItemStack(material, stack_size)

        # Insert into the next free slot:
        p.getInventory().setItem(free_stack_indices[0], stack)

        # Update next free & remaining
        free_stack_indices = free_stack_indices[1:]
        remaining_items -= stack_size
    
    p.sendMessage(
        colored_text("All done, unpacked {} items!".format(data['amount']), [ ChatColor.GREEN, ChatColor.BOLD ])
    )
    


""" Handler functions for the commands """

# TODO use localized item names - I don't think this is possible tbh
# TODO confirm transactions - Maybe possible but really hard to do with the way this plugins holds state

""" Command listeners """

@asynchronous()
def cmd_exchange(caller, params):
    # Get the name of the player that called this command
    player_name = caller.getName()

    # When should we run an update?
    # Maybe something like exchange balance

    # Start parsing the command
    command_arguments = [ str(param) for param in params ]
    subcommand = ""

    # If no args were provided - display help
    if len(command_arguments) == 0:
        print_exchange_help(player_name)
        return
    else:
        subcommand = command_arguments[0]
    
    print('Subcommand', subcommand)

    # Handle subcommands
    if subcommand == 'sell':
        handle_sell(player_name, command_arguments[1:])
        return
    elif subcommand == 'buy':
        handle_buy(player_name, command_arguments[1:])
        return
    elif subcommand == 'orders':
        handle_orderbook(player_name, command_arguments[1:])
        return
    elif subcommand == 'balance':
        handle_balance(player_name, command_arguments[1:])
        return
    elif subcommand == 'update':
        handle_update(player_name, command_arguments[1:])
        return
    elif subcommand == 'retreive':
        handle_retreive(player_name, command_arguments[1:])
        return
    elif subcommand == 'cheat':
        # Just a debug command :)
        item_stack = ItemStack(Material.GOLD_INGOT, 10)
        inventory = player(player_name).getInventory()
        inventory.addItem(item_stack)
        return
    
    player(player_name).sendMessage(
        colored_text("Unknown Subcommand: {}".format(subcommand), [ ChatColor.RED, ChatColor.ITALIC ])
    )
    print_exchange_help(player_name, display_title=False)


# Add the command -> remove is necessary because otherwise the whole thing breaks with live-reloads
remove_command('exchange')
add_command('exchange', cmd_exchange)

