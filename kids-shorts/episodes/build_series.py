"""Generate the Doodle Pals series episodes (10 series, 22 episodes) as JSON scripts.

Usage: python3 episodes/build_series.py
Writes episodes/NN-<slug>.json. File numbers interleave the series (all part 1s, then part 2s, ...)
so the daily queue never shows the same series two days in a row.
Line format: [who, spoken] or [who, spoken, shown] when the subtitle should differ (letter names).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LETTER = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', ['ay', 'bee', 'see', 'dee', 'ee', 'eff', 'jee', 'aitch', 'eye', 'jay', 'kay', 'el', 'em',
                                                 'en', 'oh', 'pee', 'cue', 'are', 'ess', 'tee', 'you', 'vee', 'double you', 'ex', 'why', 'zee']))
NUM = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
SIDE = [{"move": "penny", "x": 0.1}, {"move": "ellie", "x": 0.76}, {"move": "coco", "x": 0.9}]
CENTER = [{"move": "penny", "x": 0.3}, {"move": "ellie", "x": 0.5}, {"move": "coco", "x": 0.7}]


def intro(bg="sky"):
    return {"do": [{"bg": bg}, {"title": "Doodle Pals!"}, {"enter": "penny", "x": 0.3}, {"enter": "ellie", "x": 0.5}, {"enter": "coco", "x": 0.7}, {"confetti": 4}],
            "say": [["narrator", "Hello, friends! Welcome to Doodle Pals!"], ["penny", "Hi! I'm Penny!"], ["ellie", "I'm Ellie!"], ["coco", "And I'm Coco!"]]}


def outro(who, line):
    return {"do": [{"clear": True}, {"title": "Bye bye, friends!"}, *CENTER, {"confetti": 5}],
            "say": [[who, line], ["ellie", "Bye bye!"], ["coco", "See you tomorrow!"], ["narrator", "Bye bye, friends!"]]}


def songs(song, who):
    return [{"do": [{"clear": True}, {"title": "Let's sing!"}, *CENTER, {"confetti": 12}, {"song": True}], "say": song, "gap": 0.6},
            {"do": [{"title": "Sing it again!"}, {"confetti": 10}, {"song": True}], "say": [[who, "Sing it again!"]] + song, "gap": 0.6}]


def story(title, lines):
    return {"do": [{"title": title}], "say": lines}


def an(w):
    return 'an' if w[0].lower() in 'aeiou' else 'a'


# ---------------- reusable segments ----------------
def letter_segment(L, art, word, i, who='coco'):
    n = LETTER[L]
    beats = [{"do": [{"clear": True}, {"title": f"Letter {L}!"}, *SIDE, {"draw": f"abc-{L.lower()}", "id": f"d{L}", "x": 0.33, "y": 0.45, "s": 0.55}],
              "say": [["narrator", f"This is big {n}.", f"This is big {L}."]], "min": 4.2},
             {"do": [{"show": art, "id": f"o{L}", "x": 0.6, "y": 0.47, "s": 0.4}],
              "say": [["narrator", f"{n.capitalize()} is for {word}!", f"{L} is for {word}!"], [who, f"{n.capitalize()}, {n}, {word}!", f"{L}, {L.lower()}, {word}!"]]}]
    if i % 2 == 1:
        beats.append({"do": [{"title": "Your turn!"}, {"pulse": f"o{L}"}], "say": [["ellie", f"Can you say {word}?"], ["pause", "2"], ["ellie", f"{word.capitalize()}! Great job!"]]})
    return beats


def count_segment(art, things, n, sid, who='ellie'):
    s = 0.3 if n <= 4 else 0.24 if n <= 6 else 0.19
    dx = min(0.13, 0.62 / max(1, n - 1))
    x0 = round(0.5 - dx * (n - 1) / 2, 3)
    return [{"do": [{"clear": True}, {"title": f"Count the {things}!"}, *SIDE], "say": [[who, f"Let's count the {things}!"]]},
            {"do": [{"count": {"id": sid, "art": art, "n": n, "x0": x0, "dx": round(dx, 3), "y": 0.45, "s": s}}],
             "say": [["narrator", NUM[k].capitalize() + "!"] for k in range(1, n + 1)] + [["narrator", f"{NUM[n].capitalize()} {things}!"]], "gap": 0.4},
            {"do": [{"title": "How many?"}, {"pulse": sid}], "say": [["coco", f"How many {things}?"], ["pause", "2"], ["coco", f"{NUM[n].capitalize()}! Super counting!"]]}]


def guess_animal(art, name, snd, s1, i):
    return [{"do": [{"clear": True}, {"title": f"Who says {s1}?"}, *SIDE], "say": [["animal", snd], ["narrator", f"Who says {s1}?"], ["pause", "2"]]},
            {"do": [{"show": art, "id": f"a{i}", "x": 0.45, "y": 0.47, "s": 0.5}, {"title": f"It's {an(name)} {name}!"}],
             "say": [["narrator", f"It's {an(name)} {name}! The {name} says {s1}!"], ["animal", snd]]}]


def show_item(art, sid, title, lines, x=0.45, y=0.47, s=0.5):
    return {"do": [{"clear": True}, {"show": art, "id": sid, "x": x, "y": y, "s": s}, {"title": title}, *SIDE], "say": lines}


def quiz(art, sid, q, a, who='coco'):
    return {"do": [{"clear": True}, {"show": art, "id": sid, "x": 0.45, "y": 0.47, "s": 0.5}, {"title": q}], "say": [[who, q], ["pause", "2"], [who, a]]}


EPISODES = []


def ep(series, part, slug, title, emoji, learn, hashtags, beats):
    EPISODES.append({"series": series, "part": part, "slug": slug, "title": title, "emoji": emoji, "learn": learn, "hashtags": hashtags, "beats": beats})


# ======================= 1. ABC Adventures (K–Z) =======================
ABC = {'K': ('diamond-kite', 'kite'), 'L': ('abc-l', 'lemon'), 'M': ('abc-m', 'moon'), 'N': ('abc-n', 'nest'), 'O': ('circle-orange', 'orange'),
       'P': ('triangle-pizza', 'pizza'), 'Q': ('abc-q', 'queen'), 'R': ('square-robot', 'robot'), 'S': ('circle-sun', 'sun'), 'T': ('triangle-tree', 'tree'),
       'U': ('abc-u', 'umbrella'), 'V': ('abc-v', 'van'), 'W': ('abc-w', 'watermelon'), 'X': ('abc-x', 'xylophone'), 'Y': ('abc-y', 'yo-yo'), 'Z': ('abc-z', 'zebra')}
for part, (letters, story_l, sing) in enumerate([
    ('KLMNO', [["penny", "Let's go on an A B C adventure!"], ["coco", "Today we learn K, L, M, N and O!"]],
     [["narrator", "K for kite and L for lemon!", "K for kite and L for lemon!"], ["narrator", "M for moon, N for nest!"], ["narrator", "O for orange, we did our best!"]]),
    ('PQRST', [["ellie", "The A B C train is back!"], ["penny", "Today: P, Q, R, S and T!"]],
     [["narrator", "P for pizza, Q for queen!"], ["narrator", "R for robot, shiny and clean!"], ["narrator", "S for sun and T for tree!"], ["narrator", "Learning letters, one, two, three!"]]),
    ('UVWXYZ', [["coco", "These are the last letters of the alphabet!"], ["ellie", "U, V, W, X, Y and Z!"]],
     [["narrator", "U for umbrella, V for van!"], ["narrator", "W for watermelon, catch it if you can!"], ["narrator", "X, Y, Z, xylophone, yo-yo, zebra too!"], ["narrator", "Now we know our A B C's, hooray for you!"]]),
], start=1):
    B = [intro(), story("ABC Adventures!", story_l)]
    for i, L in enumerate(letters):
        B += letter_segment(L, ABC[L][0], ABC[L][1], i)
    B.append({"do": [{"clear": True}, {"title": "Letter quiz!"}, *SIDE], "say": [["coco", "Letter quiz time!"]]})
    for L in letters[::2][:3]:
        art, word = ABC[L]
        B.append({"do": [{"clear": True}, {"show": art, "id": f"q{L}", "x": 0.45, "y": 0.45, "s": 0.5}, {"title": f"{word.capitalize()}!"}],
                  "say": [["coco", f"What letter does {word} start with?"], ["pause", "2"], ["coco", f"{LETTER[L].capitalize()}! {LETTER[L].capitalize()} is for {word}!", f"{L}! {L} is for {word}!"]]})
    B += songs(sing, 'penny')
    B.append(outro('penny', "We learned so many letters today!"))
    ep("ABC Adventures", part, f"abc-{letters[0].lower()}-{letters[-1].lower()}", f"ABC Adventures: Letters {letters[0]} to {letters[-1]}", "🔤",
       [f"the letters {letters[0]} to {letters[-1]}", "first words", "phonics"], ["abc", "alphabet", "phonics"], B)

# ======================= 2. Counting to Ten =======================
for part, (items, story_l) in enumerate([
    ([("abc-a", "apples", 6), ("circle-cookie", "cookies", 7), ("oval-balloon", "balloons", 8)],
     [["ellie", "I can count to five. Can we count higher?"], ["penny", "Yes! Let's count to six, seven and eight!"]]),
    ([("circle-orange", "oranges", 9), ("star-starfish", "stars", 10)],
     [["coco", "Let's count all the way to ten!"], ["ellie", "Ten is a big number!"]]),
], start=1):
    B = [intro(), story("Counting to Ten!", story_l)]
    for i, (art, things, n) in enumerate(items):
        B += count_segment(art, things, n, f"c{i}")
    B.append({"do": [{"title": "Count with me!"}, {"pulse": f"c{len(items) - 1}"}],
              "say": [["penny", "Count with me, nice and fast!"], ["narrator", ", ".join(NUM[1:items[-1][2] + 1]).capitalize() + "!"], ["penny", "Hooray!"]]})
    song = [["narrator", "One, two, three, four, five!"], ["narrator", "Six, seven, eight, we feel alive!"], ["narrator", "Nine and ten, let's count again!"], ["narrator", "Counting is fun with all my friends!"]]
    B += songs(song, 'ellie')
    B.append(outro('ellie', "Now I can count to ten!"))
    ep("Counting to Ten", part, f"count-to-ten-{part}", f"Counting to Ten! Part {part}", "🔢",
       ["counting to ten" if part == 2 else "counting to eight", "numbers", "number words"], ["counting", "numbers", "counttoten"], B)

# ======================= 3. Big and Small (opposites) =======================
PAIRS1 = [("circle-sun", "sun"), ("animal-cow", "cow"), ("oval-balloon", "balloon"), ("abc-a", "apple")]
B = [intro(), story("Big and Small!", [["coco", "Look! Some things are big, and some things are small!"], ["penny", "Let's find out which is which!"]])]
for i, (art, name) in enumerate(PAIRS1):
    B.append({"do": [{"clear": True}, {"show": art, "id": f"b{i}", "x": 0.33, "y": 0.47, "s": 0.6}, {"show": art, "id": f"s{i}", "x": 0.63, "y": 0.55, "s": 0.22}, {"title": "Big and small!"}, *SIDE],
              "say": [["narrator", f"A big {name}!"], ["narrator", f"And a small {name}!"]]})
    B.append({"do": [{"title": "Which one is big?" if i % 2 == 0 else "Which one is small?"}, {"pulse": f"b{i}" if i % 2 == 0 else f"s{i}"}],
              "say": [["ellie", f"Which {name} is {'big' if i % 2 == 0 else 'small'}?"], ["pause", "2"], ["ellie", f"This one! The {'big' if i % 2 == 0 else 'small'} {name}!"]]})
B += songs([["narrator", "Big, big, big, like an elephant!"], ["narrator", "Small, small, small, like a little ant!"], ["narrator", "Big and small, small and big!"], ["narrator", "Let's all dance a happy jig!"]], 'coco')
B.append(outro('coco', "Big or small, we love them all!"))
ep("Opposites", 1, "big-and-small", "Big and Small! Opposites for Kids", "🐘", ["big and small", "opposites", "describing words"], ["opposites", "bigandsmall"], B)

B = [intro(), story("Up and Down!", [["penny", "Some things are up high, and some things are down low!"], ["ellie", "Let's look up, and look down!"]])]
for i, (up, upn, down, downn) in enumerate([("circle-sun", "sun", "animal-frog", "frog"), ("diamond-kite", "kite", "abc-f", "fish"), ("abc-m", "moon", "animal-mouse", "mouse")]):
    B.append({"do": [{"clear": True}, {"show": up, "id": f"u{i}", "x": 0.4, "y": 0.2, "s": 0.32}, {"title": "Up!"}, *SIDE],
              "say": [["narrator", f"Look up! The {upn} is up high!"]]})
    B.append({"do": [{"show": down, "id": f"w{i}", "x": 0.55, "y": 0.72, "s": 0.32}, {"title": "Down!"}], "say": [["narrator", f"Look down! The {downn} is down low!"]]})
    B.append({"do": [{"title": "Up or down?"}, {"pulse": f"u{i}"}], "say": [["coco", f"Is the {upn} up, or down?"], ["pause", "2"], ["coco", "Up! Up high!"]]})
B += songs([["narrator", "Up, up, up, reach for the sky!"], ["narrator", "Down, down, down, touch your toes, oh my!"], ["narrator", "Up and down, all around!"], ["narrator", "Jump up high, then touch the ground!"]], 'ellie')
B.append(outro('ellie', "Up and down, that was fun!"))
ep("Opposites", 2, "up-and-down", "Up and Down! Opposites Song", "⬆️", ["up and down", "opposites", "position words"], ["opposites", "upanddown"], B)

# ======================= 4. Coco's Fruit Shop =======================
FRUITS = [("abc-a", "apple", "red"), ("circle-orange", "orange", "orange"), ("abc-l", "lemon", "yellow"), ("abc-g", "grapes", "purple"), ("heart-strawberry", "strawberry", "red"), ("abc-w", "watermelon", "green and red")]
B = [intro(), story("Coco's Fruit Shop!", [["coco", "Welcome to my fruit shop!"], ["penny", "Yummy! What fruits do you have?"]])]
for i, (art, name, col) in enumerate(FRUITS[:4]):
    B.append(show_item(art, f"f{i}", f"{an(name).capitalize()} {name}!" if name != 'grapes' else "Grapes!",
                       [["coco", f"This is {an(name)} {name}!" if name != 'grapes' else "These are grapes!"], ["narrator", f"What colour is it?"], ["pause", "2"], ["narrator", f"{col.capitalize()}!"]]))
B.append({"do": [{"clear": True}, {"title": "Fruit quiz!"}], "say": [["ellie", "Fruit quiz! Can you name these fruits?"]]})
for i, (art, name, col) in enumerate(FRUITS[4:]):
    B.append(quiz(art, f"fq{i}", "What fruit is this?", f"{an(name).capitalize()} {name}! Yummy!"))
B += songs([["narrator", "Apples, oranges, lemons too!"], ["narrator", "Grapes and strawberries, just for you!"], ["narrator", "Fruit is yummy, fruit is sweet!"], ["narrator", "Fruit is good for us to eat!"]], 'coco')
B.append(outro('coco', "Thank you for visiting my fruit shop!"))
ep("Coco's Fruit Shop", 1, "fruit-shop", "Coco's Fruit Shop! Fruit Names Song", "🍎", ["fruit names", "colors", "healthy food"], ["fruits", "fruitnames", "healthyfood"], B)

B = [intro(), story("Shopping time!", [["penny", "Coco, I want to buy some fruit, please!"], ["coco", "Of course! Let's count them!"]])]
for i, (art, things, n) in enumerate([("abc-a", "apples", 3), ("circle-orange", "oranges", 4), ("abc-l", "lemons", 2)]):
    B += count_segment(art, things, n, f"c{i}", who='coco')
B.append(story("Thank you!", [["penny", "Thank you, Coco!"], ["coco", "You're welcome, Penny!"], ["narrator", "When someone helps us, we say thank you!"]]))
B += songs([["narrator", "Three red apples in my bag!"], ["narrator", "Four oranges, I'm so glad!"], ["narrator", "Two yellow lemons, one, two!"], ["narrator", "Thank you, Coco, thank you!"]], 'penny')
B.append(outro('penny', "Shopping with friends is fun!"))
ep("Coco's Fruit Shop", 2, "fruit-shopping", "Fruit Shopping! Counting and Saying Thank You", "🧺", ["counting fruit", "fruit names", "saying thank you"], ["fruits", "counting", "manners"], B)

# ======================= 5. Kind Friends (manners & feelings) =======================
B = [intro(), story("Please and Thank You!", [["ellie", "Penny, give me a cookie!"], ["penny", "Hmm, what is the magic word, Ellie?"], ["ellie", "Oh! Please! Can I have a cookie, please?"]])]
B.append(show_item("circle-cookie", "k1", "Please!", [["penny", "Of course! Here you go!"], ["ellie", "Thank you, Penny!"], ["narrator", "When we ask for something, we say please."]]))
B.append(quiz("circle-cookie", "k2", "What is the magic word?", "Please! Well done!", who='narrator'))
B.append(show_item("abc-j", "j1", "Thank you!", [["coco", "Ellie, would you like some juice?"], ["ellie", "Yes, please!"], ["narrator", "And when someone gives us something, we say..."], ["pause", "2"], ["narrator", "Thank you!"]]))
B.append({"do": [{"title": "Your turn!"}], "say": [["coco", "Can you say please?"], ["pause", "1.5"], ["coco", "Can you say thank you?"], ["pause", "1.5"], ["coco", "Wonderful manners!"]]})
B += songs([["narrator", "Please and thank you, magic words!"], ["narrator", "Say them to your friends and birds!"], ["narrator", "Please when asking, thank you when you get!"], ["narrator", "The kindest words we never forget!"]], 'ellie')
B.append(outro('ellie', "Please and thank you are magic words!"))
ep("Kind Friends", 1, "please-thank-you", "Please and Thank You! Good Manners for Kids", "🙏", ["saying please", "saying thank you", "good manners"], ["manners", "pleaseandthankyou", "kindness"], B)

B = [intro(), story("Sharing is caring!", [["penny", "I have four cookies!"], ["ellie", "Ooh, cookies! I don't have any..."], ["penny", "Let's share! Sharing is caring!"]])]
B += count_segment("circle-cookie", "cookies", 4, "sc", who='penny')
B.append(story("Two for you!", [["penny", "Two cookies for me, and two cookies for you, Ellie!"], ["ellie", "Thank you, Penny! You are so kind!"], ["narrator", "When we share, everybody is happy!"]]))
B += count_segment("abc-a", "apples", 6, "sa", who='coco')
B.append(story("Share with friends!", [["coco", "Six apples for three friends. Two each!"], ["narrator", "Can you share your toys with a friend today?"], ["pause", "2"]]))
B += songs([["narrator", "Sharing, sharing, sharing is caring!"], ["narrator", "One for you and one for me!"], ["narrator", "Sharing makes us happy, you'll see!"], ["narrator", "Sharing, sharing, sharing is caring!"]], 'penny')
B.append(outro('penny', "Sharing with friends makes me happy!"))
ep("Kind Friends", 2, "sharing-is-caring", "Sharing is Caring! Kindness Song for Kids", "🤝", ["sharing", "kindness", "counting"], ["sharing", "kindness", "manners"], B)

B = [intro(), story("I'm sorry!", [["coco", "Look at my beautiful balloon picture!"]])]
B.append({"do": [{"show": "oval-balloon", "id": "pic", "x": 0.45, "y": 0.47, "s": 0.5}, *SIDE], "say": [["penny", "It's so pretty, Coco!"]]})
B.append({"do": [{"move": "ellie", "x": 0.55}, {"erase": "pic"}, {"title": "Oops!"}], "say": [["ellie", "Oops! I erased your picture by mistake!"], ["coco", "Oh no! My picture!"]]})
B.append(story("Say sorry", [["ellie", "I'm sorry, Coco. I didn't mean to."], ["coco", "That's okay, Ellie. Thank you for saying sorry."], ["narrator", "When we make a mistake, we say sorry."]]))
B.append({"do": [{"unerase": "pic"}, {"move": "ellie", "x": 0.76}, {"title": "Let's fix it!"}], "say": [["ellie", "Let me help you draw it again!"], ["coco", "Look! It's even better now!"]]})
B.append({"do": [{"title": "What do we say?"}, {"pulse": "pic"}], "say": [["narrator", "When we make a mistake, what do we say?"], ["pause", "2"], ["narrator", "I'm sorry! Great job!"]]})
B += songs([["narrator", "Everybody makes mistakes, it's true!"], ["narrator", "Say I'm sorry, I'll help you!"], ["narrator", "Friends forgive and friends are kind!"], ["narrator", "Being friends is so fine!"]], 'coco')
B.append(outro('coco', "Friends forgive each other!"))
ep("Kind Friends", 3, "saying-sorry", "Ellie Says Sorry! Learning to Say I'm Sorry", "💗", ["saying sorry", "forgiving", "friendship"], ["kindness", "sorry", "friendship"], B)

# ======================= 6. Weather Friends =======================
B = [intro(), story("What's the weather?", [["coco", "Let's look outside! What's the weather today?"]])]
B.append(show_item("circle-sun", "w1", "Sunny!", [["narrator", "The sun is shining! It's sunny!"], ["penny", "On sunny days, we play outside!"]]))
B.append(show_item("abc-u", "w2", "Rainy!", [["narrator", "Drip, drop! It's raining! It's rainy!"], ["ellie", "On rainy days, we use an umbrella!"]]))
B.append(quiz("circle-sun", "q1", "Is it sunny or rainy?", "Sunny! The sun is shining!"))
B.append(quiz("abc-u", "q2", "What do we need when it rains?", "An umbrella! Great job!"))
B += songs([["narrator", "Sunny, sunny, sun is bright!"], ["narrator", "Rainy, rainy, umbrella tight!"], ["narrator", "What's the weather, can you say?"], ["narrator", "Let's look outside, every day!"]], 'coco')
B.append(outro('coco', "Rain or sun, we have fun!"))
ep("Weather Friends", 1, "sunny-and-rainy", "Sunny and Rainy! Weather Song for Kids", "☀️", ["weather words", "sunny and rainy", "umbrella"], ["weather", "sunny", "rainy"], B)

B = [intro(), story("Windy day!", [["penny", "Whoosh! Can you hear the wind?"], ["ellie", "It's a windy day! Let's fly a kite!"]])]
B.append(show_item("diamond-kite", "k", "Windy!", [["narrator", "On windy days, kites fly high in the sky!"], ["narrator", "Whoosh, whoosh!"]], y=0.3))
B.append(story("Day and night", [["coco", "When the sun goes down, it gets dark."], ["narrator", "It's night time!"]]))
B.append(show_item("abc-m", "m", "Night!", [["narrator", "At night, we see the moon!"], ["penny", "Good night, moon!"]], y=0.3))
B.append(quiz("circle-sun", "q1", "Do we see the sun in the day, or at night?", "In the day!"))
B.append(quiz("abc-m", "q2", "When do we see the moon?", "At night! Good night, moon!"))
B += songs([["narrator", "The wind goes whoosh, the kite flies high!"], ["narrator", "The sun says hello in the morning sky!"], ["narrator", "The moon comes out when it is night!"], ["narrator", "Good night, moon, sleep tight!"]], 'penny')
B.append(outro('penny', "Good night, friends! Sleep tight!"))
ep("Weather Friends", 2, "windy-day-and-night", "Windy Day and Good Night Moon! Weather Song", "🌙", ["windy weather", "day and night", "sun and moon"], ["weather", "dayandnight", "goodnight"], B)

# ======================= 7. Animal Homes =======================
FARM = [("animal-cow", "cow", "Moo!", "moo"), ("animal-pig", "pig", "Oink oink!", "oink"), ("animal-chicken", "chicken", "Cluck cluck!", "cluck"), ("animal-horse", "horse", "Neigh!", "neigh")]
PETS = [("animal-cat", "cat", "Meow!", "meow"), ("animal-dog", "dog", "Woof woof!", "woof"), ("animal-mouse", "mouse", "Squeak squeak!", "squeak")]
WILD = [("animal-lion", "lion", "Roar!", "roar"), ("animal-owl", "owl", "Hoo hoo!", "hoo"), ("animal-frog", "frog", "Ribbit!", "ribbit")]
B = [intro(), story("Farm animals!", [["ellie", "Where do animals live?"], ["coco", "Some animals live on a farm!"]])]
for i, a in enumerate(FARM):
    B += guess_animal(*a, i)
B.append(story("Pets at home!", [["penny", "Some animals live at home with us. They are pets!"]]))
for i, a in enumerate(PETS):
    B += guess_animal(*a, 10 + i)
B += songs([["narrator", "On the farm, the cow says moo!"], ["narrator", "The pig says oink, the horse says neigh too!"], ["narrator", "At home, the cat says meow!"], ["narrator", "The dog says woof, take a bow!"]], 'ellie')
B.append(outro('ellie', "I love all the animals!"))
ep("Animal Homes", 1, "farm-and-pets", "Farm Animals and Pets! Animal Sounds Song", "🐄", ["farm animals", "pets", "animal sounds"], ["animals", "farmanimals", "pets"], B)

B = [intro(), story("Wild animals!", [["coco", "Some animals live in the wild, in jungles, forests and ponds!"], ["penny", "Let's listen carefully!"]])]
for i, a in enumerate(WILD):
    B += guess_animal(*a, i)
B.append({"do": [{"clear": True}, {"title": "Farm, pet or wild?"}], "say": [["ellie", "Let's play a game! Farm, pet, or wild?"]]})
for i, (art, name, where) in enumerate([("animal-cow", "cow", "the farm"), ("animal-lion", "lion", "the wild"), ("animal-cat", "cat", "home, it's a pet")]):
    B.append(quiz(art, f"g{i}", f"Where does the {name} live?", f"On {where}!" if where == "the farm" else f"In {where}!" if where == "the wild" else f"At {where}!", who='ellie'))
B += songs([["narrator", "The lion roars in the jungle wide!"], ["narrator", "The owl says hoo, the frogs hop side to side!"], ["narrator", "Farm and pets and wild ones too!"], ["narrator", "So many animals, me and you!"]], 'coco')
B.append(outro('coco', "Animals live in so many places!"))
ep("Animal Homes", 2, "wild-animals", "Wild Animals! Where Do Animals Live?", "🦁", ["wild animals", "animal homes", "animal sounds"], ["animals", "wildanimals", "animalsounds"], B)

# ======================= 8. Music Time =======================
B = [intro("party"), story("Music time!", [["penny", "Let's make music!"], ["coco", "I have a xylophone!"]])]
B.append(show_item("abc-x", "x", "Xylophone!", [["narrator", "This is a xylophone. Ding, ding, ding!"], ["coco", "Each bar has a different colour!"]]))
B.append({"do": [{"title": "Clap with me!"}], "say": [["ellie", "Let's clap! Clap, clap, clap!"], ["narrator", "Clap three times!"], ["pause", "2"], ["narrator", "Now stomp your feet! Stomp, stomp!"], ["pause", "2"]]})
B += count_segment("abc-x", "xylophones", 3, "cx", who='penny')
B.append({"do": [{"title": "Loud and quiet!"}], "say": [["narrator", "Let's sing loud! LA LA LA!"], ["narrator", "Now quiet... la, la, la."], ["coco", "Loud and quiet! Opposites!"]]})
B += songs([["narrator", "Clap your hands, one, two, three!"], ["narrator", "Stomp your feet and sing with me!"], ["narrator", "Ding, ding, ding, the xylophone sings!"], ["narrator", "Music is one of my favourite things!"]], 'coco')
B.append(outro('coco', "Music makes me happy!"))
ep("Music Time", 1, "clap-and-sing", "Music Time! Clap, Stomp and Sing", "🎶", ["music words", "loud and quiet", "clapping and counting"], ["music", "kidssongs", "clap"], B)

B = [intro("party"), story("Animal band!", [["ellie", "Let's make an animal band!"], ["penny", "Everyone sings their own sound!"]])]
for i, a in enumerate([FARM[0], FARM[2], PETS[1], WILD[2]]):
    B += guess_animal(*a, i)
B.append({"do": [{"clear": True}, {"title": "Sing together!"}, {"show": "animal-cow", "id": "b1", "x": 0.3, "y": 0.45, "s": 0.3}, {"show": "animal-chicken", "id": "b2", "x": 0.45, "y": 0.45, "s": 0.3}, {"show": "animal-dog", "id": "b3", "x": 0.6, "y": 0.45, "s": 0.3}, {"pulse": "b1"}, {"pulse": "b2"}, {"pulse": "b3"}],
          "say": [["animal", "Moo! Cluck cluck! Woof woof!"], ["narrator", "What a noisy band!"]]})
B += songs([["narrator", "Moo goes the cow in the animal band!"], ["narrator", "Cluck goes the chicken, isn't it grand!"], ["narrator", "Woof goes the dog, ribbit goes the frog!"], ["narrator", "Everybody sing, sing along!"]], 'ellie')
B.append(outro('ellie', "Our animal band is the best!"))
ep("Music Time", 2, "animal-band", "The Animal Band! Animal Sounds Song", "🥁", ["animal sounds", "music", "singing together"], ["music", "animalsounds", "kidssongs"], B)

# ======================= 9. Shape Sort =======================
B = [intro(), story("Shape sort!", [["coco", "Let's sort things by shape!"], ["penny", "First, round things! Circles!"]])]
for i, (art, name) in enumerate([("circle-sun", "sun"), ("circle-cookie", "cookie"), ("circle-orange", "orange"), ("abc-y", "yo-yo")]):
    B.append(show_item(art, f"c{i}", "A circle!", [["narrator", f"The {name} is round. It's a circle!"]]))
B.append(story("Triangles!", [["ellie", "Now, things with three sides! Triangles!"]]))
for i, (art, name) in enumerate([("triangle-pizza", "pizza slice"), ("triangle-tree", "tree")]):
    B.append(show_item(art, f"t{i}", "A triangle!", [["narrator", f"The {name} has three sides. It's a triangle!"]]))
B.append(quiz("circle-orange", "q1", "Circle or triangle?", "A circle! It's round!"))
B.append(quiz("triangle-pizza", "q2", "Circle or triangle?", "A triangle! Three sides!"))
B += songs([["narrator", "Round and round, a circle goes!"], ["narrator", "Sun and cookies, everyone knows!"], ["narrator", "One, two, three, a triangle!"], ["narrator", "Pizza and trees, look and see!"]], 'coco')
B.append(outro('coco', "Circles and triangles are everywhere!"))
ep("Shape Sort", 1, "circles-and-triangles", "Circles and Triangles! Shape Sorting for Kids", "🔺", ["circles", "triangles", "sorting"], ["shapes", "circle", "triangle"], B)

B = [intro(), story("Square or rectangle?", [["penny", "Squares and rectangles both have four sides!"], ["coco", "Let's find the difference!"]])]
for i, (art, name) in enumerate([("square-present", "present"), ("square-robot", "robot")]):
    B.append(show_item(art, f"s{i}", "A square!", [["narrator", f"The {name} is a square. All four sides are the same!"]]))
for i, (art, name) in enumerate([("rectangle-door", "door"), ("abc-j", "juice box")]):
    B.append(show_item(art, f"r{i}", "A rectangle!", [["narrator", f"The {name} is a rectangle. Two long sides, and two short sides!"]]))
B.append({"do": [{"clear": True}, {"title": "Let's draw!"}, *SIDE, {"draw": "square-present", "id": "dr", "x": 0.42, "y": 0.45, "s": 0.55}], "say": [["narrator", "Let's draw a square together! One, two, three, four sides!"]], "min": 4.2})
B.append(quiz("rectangle-door", "q1", "Square or rectangle?", "A rectangle! Two long sides!"))
B.append(quiz("square-present", "q2", "Square or rectangle?", "A square! All sides the same!"))
B += songs([["narrator", "A square has four sides, all the same!"], ["narrator", "A present, a robot, that's its name!"], ["narrator", "A rectangle is long, like a door!"], ["narrator", "Four sides each, let's find some more!"]], 'penny')
B.append(outro('penny', "Now I know squares and rectangles!"))
ep("Shape Sort", 2, "squares-and-rectangles", "Squares and Rectangles! What's the Difference?", "🟦", ["squares", "rectangles", "comparing shapes"], ["shapes", "square", "rectangle"], B)

# ======================= 10. What's Missing? (memory game) =======================
for part, sets in enumerate([
    [[("abc-a", "apple"), ("circle-sun", "sun"), ("oval-balloon", "balloon")], [("animal-cat", "cat"), ("animal-dog", "dog"), ("animal-duck", "duck")]],
    [[("abc-l", "lemon"), ("diamond-kite", "kite"), ("abc-m", "moon")], [("square-robot", "robot"), ("triangle-tree", "tree"), ("abc-e", "egg")], [("animal-pig", "pig"), ("animal-frog", "frog"), ("animal-owl", "owl")]],
], start=1):
    B = [intro(), story("What's missing?", [["ellie", "Let's play my favourite game: What's missing!"], ["ellie", "Look carefully. I will erase one thing!"]])]
    for r, trio in enumerate(sets):
        ids = [f"m{r}{k}" for k in range(3)]
        do = [{"clear": True}, {"title": "Look carefully!"}, *SIDE] + [{"show": art, "id": ids[k], "x": 0.25 + k * 0.2, "y": 0.45, "s": 0.3} for k, (art, _) in enumerate(trio)]
        B.append({"do": do, "say": [["narrator", f"{an(trio[0][1]).capitalize()} {trio[0][1]}, {an(trio[1][1])} {trio[1][1]}, and {an(trio[2][1])} {trio[2][1]}."], ["narrator", "Close your eyes!"], ["pause", "1.5"]]})
        miss = (r + part) % 3
        B.append({"do": [{"erase": ids[miss]}, {"title": "What's missing?"}, {"move": "ellie", "x": 0.6}], "say": [["ellie", "Erase, erase! Open your eyes!"], ["narrator", "What's missing?"], ["pause", "2.5"]]})
        B.append({"do": [{"unerase": ids[miss]}, {"move": "ellie", "x": 0.76}, {"title": f"The {trio[miss][1]}!"}], "say": [["ellie", f"The {trio[miss][1]}! You found it!"]]})
    B += songs([["narrator", "Look, look, look with your eyes!"], ["narrator", "Something's missing, what a surprise!"], ["narrator", "Think and think, what can it be?"], ["narrator", "You found it, one, two, three!"]], 'ellie')
    B.append(outro('ellie', "You have super memory!"))
    ep("What's Missing?", part, f"whats-missing-{part}", f"What's Missing? Memory Game Part {part}", "🔍", ["memory", "observation", "naming objects"], ["memorygame", "brainteaser", "kidsgames"], B)

# ---------------- write files, interleaving series ----------------
start = 9
order = sorted(EPISODES, key=lambda e: (e["part"], [s["series"] for s in EPISODES].index(e["series"])))
for n, e in enumerate(order, start=start):
    eid = f"{n:02d}-{e['slug']}"
    out = {"id": eid, "series": e["series"], "part": e["part"], "title": e["title"], "emoji": e["emoji"], "learn": e["learn"], "hashtags": e["hashtags"], "beats": e["beats"]}
    json.dump(out, open(os.path.join(HERE, eid + ".json"), "w"), indent=1, ensure_ascii=False)
    print(eid, "-", e["series"], "part", e["part"])
