# API request library
import webbrowser
import requests
import urllib.request
# Interface to TK Gui toolkit
import tkinter
from tkinter import *
# Tk themed widget set - overrides Tk widgets with modern versions
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from typing import Any
from tktooltip import ToolTip
from tkinter import messagebox
from PIL import Image, ImageTk

# Global variables
# Version number as string to display
VERSION_NUM = "Version - 1.7"
# This is the application ID and app KEY you should send with each API request.
APP_ID = '3a6ebb3f'
APP_KEY = '3c298096d79eb8a9551ece6adff2f8e7'
current_recipe_num: int = 0
total_recipes: int = 0
edmamam_count: int = 0  # Total number of results according to Edamam
recipe_hits = []
recipe_img = Image.open("images/Hungry_Horace_icon.jpg")

# List of health options
health_opt_list: list[str | Any] = ["none",
                                    "alcohol-cocktail",
                                    "alcohol-free",
                                    "celery-free",
                                    "crustacean-free",
                                    "dairy-free",
                                    "egg-free",
                                    "fish-free",
                                    "fodmap-free",
                                    "gluten-free",
                                    "immuno-supportive",
                                    "keto-friendly",
                                    "kidney-friendly",
                                    "kosher",
                                    "low-potassium",
                                    "low-sugar",
                                    "lupine-free",
                                    "mollusk-free",
                                    "mustard-free",
                                    "No-oil-added",
                                    "paleo",
                                    "peanut-free",
                                    "pescatarian",
                                    "pork-free",
                                    "red-meat-free",
                                    "sesame-free",
                                    "shellfish-free",
                                    "soy-free",
                                    "sugar-conscious",
                                    "sulfite-free",
                                    "tree-nut-free",
                                    "vegan",
                                    "vegetarian",
                                    "wheat-free"]
root = Tk()

root.title("Hungry Horace - Recipe Hunter")
root.geometry("700x450")
frm = Frame(root, padding=10)
frm.grid()


#  This function will need to use 'ingredient' to build the search URL and return the json recipe_hits
def search_api(ingredient, health_opt):
    # Old API URL - doesn't work with health option but useful for testing
    # url = "https://api.edamam.com/search?q={0}&app_id={1}&app_key={2}".format(ingredient, APP_ID, APP_KEY)
    # New API URLs
    # Use simple URL without health option if none chosen
    if health_opt == "none" or health_opt == "":
        url = "https://api.edamam.com/api/recipes/v2?type=public&q={0}&app_id={1}&app_key={2}". \
           format(ingredient.lower(), APP_ID, APP_KEY)
    else:  # Call API with health option
        url = "https://api.edamam.com/api/recipes/v2?type=public&q={0}&app_id={1}&app_key={2}&health={3}". \
            format(ingredient.lower(), APP_ID, APP_KEY, health_opt.lower())

    response = requests.get(url)
    # 200 should be success, 400s for errors
    if response.status_code >= 400:
        messagebox.showerror('API Error', 'Error' + str(response.status_code))
    json_data = response.json()
    assert isinstance(recipe_hits, object)

    return json_data


def new_search(ingredient, health_opt):
    # Ensure that user entry is valid before API request
    if ingredient.isalpha() and ingredient != "":
        api_return = search_api(ingredient, health_opt)
        # TODO - distinguish between 404 and other errors
        try:
            global total_recipes
            total_recipes = api_return['to']
            # Even with a 200 status code, there may be zero recipes returned
            if total_recipes < 1:
                messagebox.showerror('Type error', '404 - not found \n Please try again.')
                return
            global edmamam_count
            edmamam_count = api_return['count']
            global recipe_hits
            recipe_hits = api_return['hits']
        except TypeError:
            messagebox.showerror('Type error', '404 - not found')
            print(api_return[0])  # Log error information
        except ValueError:
            messagebox.showerror('Value error', '404 - not found')
            print(api_return[0])  # Log error information
        else:
            # Use this to keep track of where we are in the list of recipe hits
            global current_recipe_num
            current_recipe_num = 0
            change_recipe()
            prev_btn['state'] = 'disabled'
            if total_recipes > 1:
                next_btn['state'] = 'normal'
                url_btn['state'] = 'normal'
    else:
        messagebox.showerror('Error', "Please enter only letters from A-Z, no numbers or special symbols")


def change_recipe():
    recipe_title = get_label()
    title_lbl.config(text=recipe_title)
    # Re-enable the text widget to add new recipe
    txt_widget['state'] = 'normal'
    # Delete any existing text first
    txt_widget.delete(0.0, END)
    # Output text to the text box
    # Display recipe x of y (from z results) using current r num, 'to' and 'count'
    txt_widget.insert(END, "Recipe {0} of {1} from {2} web results".format(
        (current_recipe_num + 1), total_recipes, edmamam_count))
    txt_widget.insert(END, "\n\nIngredients list:\n")
    ingr_list = get_ingredients()
    for ingr_str in ingr_list:
        txt_widget.insert(END, "{0} \n".format(ingr_str))

    portion_yield = get_portion_yield()
    txt_widget.insert(END, "\nNumber of portions: {0} \n".format(portion_yield))

    txt_widget.insert(END, "\nHealth Labels:\n")
    health_labels = get_health_labels()
    for health_str in health_labels:
        txt_widget.insert(END, "{0} \n".format(health_str))

    txt_widget.insert(END, "\nURL:\n")
    url_str = get_url()
    txt_widget.insert(END, "{0} \n".format(url_str))
    txt_widget['state'] = 'disabled'

    # Upload the recipe image
    img_url = str(get_image_url())
    # Try loading image from URL
    # TODO add try and except here - if URL image fails, set to app icon
    #  or 404 placeholder image?
    urllib.request.urlretrieve(img_url, "images/recipe.jpg")
    # Tkinter PhotoImage only supports GIF, PGM, PPM & PNG
    # So we open the image file and create a PIL image object
    new_img = Image.open("images/recipe.jpg")
    new_img = new_img.resize((200, 200))
    #  Use PIL image object to create PhotoImage object
    global recipe_img
    recipe_img = ImageTk.PhotoImage(new_img)
    image_lbl.configure(image=recipe_img)


def open_url():
    recipe_url = get_url()
    webbrowser.open(recipe_url)


def next_recipe():
    global current_recipe_num
    global total_recipes
    if current_recipe_num < total_recipes:
        current_recipe_num += 1
    else:
        return

    if current_recipe_num == (total_recipes - 1):
        next_btn['state'] = 'disabled'
    if current_recipe_num > 0:
        prev_btn['state'] = 'normal'

    # Display next recipe
    change_recipe()


def prev_recipe():
    global current_recipe_num
    if current_recipe_num > 0:
        # Only enable when current_recipe_num > 0
        prev_btn['state'] = 'normal'
        current_recipe_num -= 1
        next_btn['state'] = 'normal'
        change_recipe()
    else:
        prev_btn['state'] = 'disabled'


# This function will return the recipe name
def get_label():
    label = recipe_hits[current_recipe_num]["recipe"]["label"]
    return label


# This function will return the ingredient list
def get_ingredients():
    ingredient_lines = recipe_hits[current_recipe_num]["recipe"]["ingredientLines"]
    return ingredient_lines


def get_health_labels():
    health_labels = recipe_hits[current_recipe_num]["recipe"]["healthLabels"]
    return health_labels


def get_portion_yield():
    yield_num = recipe_hits[current_recipe_num]["recipe"]["yield"]
    return yield_num


# This function will return the original URL for the recipe
def get_url():
    url = recipe_hits[current_recipe_num]["recipe"]["url"]
    return url


def get_image_url():
    img_url = recipe_hits[current_recipe_num]["recipe"]["image"]
    return img_url


# Create UI components/widgets
# Label widget
search_lbl = Label(master=frm, text="Ingredient/Keyword")  # Create label UI widget
search_lbl.grid(column=0, row=0, pady=3, sticky='w')  # Place label widget in layout grid
# Text entry field
search_txt = Entry(master=frm, name="search", width=35)
search_txt.grid(column=1, row=0, padx=0, pady=3, sticky='w')
# Tooltip prompt for ingredient text entry
ToolTip(search_txt, msg="Food ingredient/keyword to search for")

health_opt_lbl = Label(master=frm, text="Health Option")  # Create label UI widget
health_opt_lbl.grid(column=0, row=1, pady=3, sticky='w')  # Place label widget in layout grid
# Health options combobox (dropdown) list
n = StringVar()  # TODO - figure out what this is
health_opt_combo = Combobox(frm, width=30, textvariable=n, state='readonly')
health_opt_combo.grid(column=1, row=1, pady=0, sticky='w')
# Adding combobox drop down list
health_opt_combo['values'] = health_opt_list
health_opt_combo.current(0)
# Tooltip prompt for health option
ToolTip(health_opt_combo, msg="Dietary option to filter recipes")

# btn = Button(frm, text="Search", command=root.destroy).grid(column=1, row=4)
search_btn = Button(master=frm, text="New Search", command=lambda: new_search(search_txt.get(), health_opt_combo.get()))
search_btn.grid(column=0, row=2, columnspan=2, pady=3)

# Recipe title label
title_lbl = Label(frm, text="Hungry Horace - Recipe Search", font="Helvetica 12 bold", wraplength=700)
title_lbl.grid(column=0, row=3, columnspan=4, rowspan=2, sticky='w')  # Place label widget in layout grid


# Load application icon into label
app_icon = Image.open("images/Hungry_Horace_icon.jpg")
app_icon = app_icon.resize((200, 200))
recipe_img = ImageTk.PhotoImage(app_icon)
image_lbl = Label(frm, width=20, relief=tkinter.RIDGE, image=recipe_img)
image_lbl.grid(column=2, row=5, sticky='e')


# Large scrolled text window - recipe details
txt_widget = ScrolledText(master=frm, wrap=tkinter.WORD, width=50, height=15, relief=tkinter.RIDGE)
txt_widget.grid(column=0, row=5, columnspan=2, pady=4, padx=4)
# Load welcome message
txt_widget.insert(END, "Welcome to Hungry Horace, your friendly recipe hunter!\n")
txt_widget.insert(END, "\nWhat are you hungry for today?"
                       "\n\n1) Enter an ingredient/keyword to search for \n(e.g. 'cheese'/'curry')"
                       "\n2) Use the menu to add a dietary option to \nfilter recipes by."
                       "\n3) Press 'Search'")
txt_widget.insert(END, "\n\n\n\n\n{0} Copyright - Janeeta & Helen".format(VERSION_NUM))

# Recipe button to open link
url_btn = Button(frm, text="Go to recipe", command=open_url)
url_btn.grid(column=0, row=6, padx=4)
url_btn['state'] = 'disabled'

# Previous recipe button
prev_btn = Button(master=frm, text="Prev", command=prev_recipe)
prev_btn.grid(column=0, row=7, columnspan=1)
prev_btn['state'] = 'disabled'

# Next recipe button
next_btn = Button(master=frm, text="Next", command=next_recipe)
next_btn.grid(column=1, row=7, columnspan=1)
next_btn['state'] = 'disabled'

# Run
root.mainloop()
