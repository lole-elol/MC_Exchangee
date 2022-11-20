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
from datetime import date
import math
import urllib

api_base_url = "https://nxr9qbf1zf.execute-api.eu-central-1.amazonaws.com/default/hackatum-BloombergBackend-1znJQelc3f38/"

""" Constants """
order_display_header = ['Type', 'Name', 'Price', 'Amount', 'Issuer']

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
            for i, e in enumerate(row):
                col_sz[i] = max(len(str(e)), col_sz[i])

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

def parse_order(ofa):
    type = 'BUY' if ofa['side'] == 'buy' else 'SELL'
    user_name = str(ofa['ownerID']) if ofa.get('ownerID') is not None else '---'
    price = int(ofa['price'])
    item_name = str(ofa['type'])
    amount = int(ofa['quantity'])
    return [ type, item_name, price, amount, user_name]


""" API Module """

def http_get(endpoint):
    req = urllib2.Request(endpoint)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print(e)
        return e.code, None

    data = response.read()
    status = response.getcode()
    return status, data

def http_post(endpoint, body):
    print(body)
    req = urllib2.Request(endpoint, body)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print(e)
        return e.code, None
    
    data = response.read()
    status = response.getcode()
    return status, data

def get_balance(player_name):
    
    body = json.dumps({
        "ownerID": player_name
    })
    status, response = http_post(api_base_url + "balance", body)

    # Handle error conditions
    if status != 200:
        return None

    return json.loads(response)['balance']

def get_orders(search = None, page=0):

    # Since the API does not support filtering, we'll just implement it client-side
    status, body = http_get(api_base_url + "orderList")
    if status != 200:
        return None

    all_open_orders = [ 
        parse_order(order_from_api) for order_from_api 
        in json.loads(body)
    ]

    filtered_orders = []
    for order in all_open_orders:
        if search.lower() in order[1].lower():
            filtered_orders.append(order)
    
    n_pages = int(math.ceil(len(filtered_orders) / 8))
    current_page = min(page, n_pages)

    return current_page, n_pages, filtered_orders[page*8: (page+1)*8]

def create_sell_order(price, item_name, quantity, player_name):
    """ Creates a new sell order, returns a boolean indicating if everything went to plan """
    # Create the body
    body = json.dumps({
        "side": "sell",
        "price": price,
        "quantity": quantity,
        "status": 1,
        "type": item_name,
        "ownerID": player_name,
        "balanced": 0,
        "userCollected": 0
    })
    status, _ = http_post(api_base_url + "order", body)
    return status == 200

def create_buy_order(price, item_name, quantity, player_name):
    """ Creates a new buy order, returns a boolean indicating if everything went to plan """
    # Create the body
    body = json.dumps({
        "side": "buy",
        "price": price,
        "quantity": quantity,
        "status": 1,
        "type": item_name,
        "ownerID": player_name,
        "balanced": 0,
        "userCollected": 0
    })
    status, _ = http_post(api_base_url + "order", body)
    return status == 200

def collect_order(order_id):
    query_params = urllib.urlencode({
        "orderID": order_id
    })
    print(query_params)
    status, response = http_get(api_base_url + 'order?' + query_params)
    print(response)
    if status != 200:
        return None

    response = json.loads(response)[0]
    return { "id": response['orderID'], "name": response['type'], "amount": int(response['quantity']), "retreived": response['userCollected'] != 0 }

def get_updates(player_name):
    query_params = urllib.urlencode({
        "ownerID": player_name
    })
    status, response = http_get(api_base_url + 'poll?' + query_params)

    # Quick-exit when something wonky happened
    if status != 200:
        return None

    bought = []
    n_sold = 0
    sold_profit = 0

    orders = json.loads(response)
    for order in orders:
        # Status 1 -> unfullfilled
        if order['status'] != 1:
            if order['side'] == 'sell':
                n_sold += 1
                sold_profit += int(order['quantity']) * int(order['price'])
            else:
                bought.append({
                    "id": order['orderID'],
                    "name": order['type'],
                    "amount": order['quantity']
                })
    return n_sold, sold_profit, bought

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
    if balance is None:
        p.sendMessage(
            colored_text("SERVER ERROR", [ ChatColor.RED, ChatColor.BOLD ])
        )
        p.sendMessage(
            colored_text("Could not get balance, something went wrong with the server, please try again, later.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return 

    
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
    item_name = "_".join([ part.capitalize() for part in str(item_in_hand.getType()).split('_')])
    
    # Check if the count is valid:
    if sell_count is None:
        sell_count = amount_in_hand
    if amount_in_hand < sell_count:
        p.sendMessage(
            colored_text("Can't sell {} of {}, you're only holding {}".format(sell_count, item_name, amount_in_hand), [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return
    

    # Gather the data needed for the request
    material = item_in_hand.getType()

    print("Player {} wants to sell {}x{} for {} each.".format(player_name, sell_count, material, sell_price))

    # Send the request
    if not create_sell_order(sell_price, item_name, sell_count, player_name):
        p.sendMessage(
            colored_text("SERVER ERROR", [ ChatColor.RED, ChatColor.BOLD ])
        )
        p.sendMessage(
            colored_text("Could not create sell order, something went wrong with the server, please try again, later.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return 

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
    if not create_buy_order(item_price, item_name, item_amount, player_name):
        p.sendMessage(
            colored_text("SERVER ERROR", [ ChatColor.RED, ChatColor.BOLD ])
        )
        p.sendMessage(
            colored_text("Could not create buy order, something went wrong with the server, please try again, later.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return 

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
    order_info = get_orders(search, page)
    if order_info is None:
        p.sendMessage(
            colored_text("SERVER ERROR", [ ChatColor.RED, ChatColor.BOLD ])
        )
        p.sendMessage(
            colored_text("Could not get list of orders, something went wrong with the server, please try again, later.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return 

    # Extract the info, now that we know it's safe
    page, total_pages, orders = order_info


    # Calculate column sizes
    column_sizes = get_column_sizes([order_display_header] + orders)

    separator = ' || '
    # Header
    p.sendMessage(
        separator.join([
            colored_text(pad_and_center_string(h, column_sizes[i]), [ ChatColor.BOLD ]) for i, h in enumerate(order_display_header)
        ])
    )
    # Data
    for order in orders:
        tmp = []
        for i, h in enumerate(order):
            tmp.append(pad_string_right(h, column_sizes[i] + 1))
        p.sendMessage(separator.join(tmp))
    # Footer
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
    update = get_updates(player_name)

    # Handle Server errors
    if update is None:
        p.sendMessage(
            colored_text("SERVER ERROR", [ ChatColor.RED, ChatColor.BOLD ])
        )
        p.sendMessage(
            colored_text("Could not get updates, something went wrong with the server, please try again, later.", [ ChatColor.RED, ChatColor.ITALIC ])
        )
        return 
    
    n_sold, sell_profit, bought = update
    
    # Selling Stats
    p.sendMessage(
        "So far you have sold {} items, for a total profit of {}".format(
            n_sold,
            colored_text("{} $".format(sell_profit), [ ChatColor.GOLD ])
        )
    )

    # Bought but not retreived items
    if len(bought) > 0:
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
    data = collect_order(order_id)

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


