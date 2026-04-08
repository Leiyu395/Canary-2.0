init python:
    def slider_update(st):
        global slider_speed

        for sprite in slider_sprites:
            if sprite.type == "slider":
                if round(sprite.x) < slider_bar_size[0] - slider_size[0] and sprite.direction == "right":
                    sprite.x += slider_speed * food_difficulty
                    slider_speed += 0.04
                elif round(sprite.x) >= slider_bar_size[0] - slider_size[0] and sprite.direction == "right":
                    sprite.direction = "left"
                    slider_speed = 2
                elif round(sprite.x) > 0 and sprite.direction == "left":
                    sprite.x -= slider_speed * food_difficulty
                    slider_speed += 0.04
                elif round(sprite.x) == 0 and sprite.direction == "left":
                    sprite.direction = "right"
                    slider_speed = 2
        if not stop_slider:
            return 0
        else:
            return None

    def check_slider_safe_zone():
        global food_cooked
        global food_cooked_tries
        global stop_slider

        for slider in slider_sprites:
            if slider.type == "slider":
                for safe_zone in slider_sprites:
                    if safe_zone.type == "safe-zone":
                        if safe_zone.x < slider.x < safe_zone.x + safe_zone_size[0]:
                            food_cooked = True
                            stop_slider = True
                            renpy.play("audio/success.mp3", "sound")
                        elif food_cooked_tries > 0:
                            renpy.play("audio/error.ogg", "sound")
                            food_cooked_tries -= 1
                        if food_cooked_tries == 0:
                            renpy.show_screen("game_over")
                            stop_slider = True

    def reset_food_puzzle():
        global food_cooked
        global food_cooked_tries
        global stop_slider
        global slider_speed

        food_cooked = False
        food_cooked_tries = 1
        stop_slider = False
        slider_speed = 2

        for sprite in slider_sprites:
            if sprite.type == "slider":
                sprite.x = 0
            elif sprite.type == "safe-zone":
                random_x = renpy.random.randint(0, slider_bar_size[0] - safe_zone_size[0])
                sprite.x = random_x

        slider_SM.redraw(0)
        renpy.restart_interaction()
    
    def drag_placed(drags, drop):
        if not drop: 
            return 

        store.draggable = drags[0].drag_name 
        store.droppable = drop.drag_name 

        return True  

default hunger = 0
default thirst = 0
default happiness = 0  
default frame_num = 0

style stat_bar:
    left_bar Frame ("#ff9305" )
    right_bar Frame ("#fffb05")

transform small:
    zoom 0.35

transform centre:
    pos(900, 50)
    zoom 0.5

transform half_size:
    zoom 0.5

transform food_transform:
    zoom 0.5
    anchor (0.5, 0.5)
    align (0.5, 0.7)
    subpixel True
    on hover:
        easein 1.0 zoom 0.51
    on idle:
        easein 1.0 zoom 0.5

transform food_cooked_anim:
    zoom 0.5
    alpha 0.0
    parallel:
        easein 3.0 zoom 1.0
    parallel:
        easein 2.0 alpha 1.0

screen game_over:
    modal True
    key "K_SPACE" action [Function(reset_food_puzzle), Hide("game_over")]
    frame:
        background "#00000080"
        xfill True
        yfill True
        frame:
            background "#FFFFFFE6"
            xfill True
            padding (15,0)
            align (0.5, 0.5)
            text "Game Over!" color "#000000" size 34 xalign 0.5

    imagebutton:
            xanchor 0.5
            yanchor 0.5
            xpos 0.75
            ypos 0.5
            idle "continue-button.png"
            hover "continue-button.png"
            action [Play("sound", "audio/click.mp3"), Hide("displayTextScreen"), Jump("Failed_cooking")]
            hovered Show("displayTextScreen", displayText = "Oh dear...")
            unhovered Hide("displayTextScreen")

screen food_puzzle:
    on "show" action Function(reset_food_puzzle)
    key ["K_SPACE", "mousedown_1"] action If(food_cooked, true = [Hide("food_puzzle", transition = Fade(1,1,1)), Show ("Cooking_sequence")], false = Function(check_slider_safe_zone))
    image "bg shelter.png"
    if not food_cooked:
        frame:
            background "#FFFFFF"
            padding (5, 5)
            align (0.5, 0.3)
            text "Attempts Left: [food_cooked_tries]" size 18 color "#000000" text_align 0.5
        frame:
            background None
            align (0.5, 0.4)
            xysize slider_bar_size
            image "slider-bar.png" at half_size
            add slider_SM
        image "pot-idle.png" align (0.5, 0.7) at half_size
    else:
        image "pasta.png" align (0.5, 0.7) at food_cooked_anim

        imagebutton:
            xanchor 0.5
            yanchor 0.5
            xpos 0.75
            ypos 0.5
            idle "continue-button.png"
            hover "continue-button.png"
            action [Hide("displayTextScreen"), Jump("Sucessful_cooking")]
            hovered Show("displayTextScreen", displayText = "Eat the food!")
            unhovered Hide("displayTextScreen")

screen Cooking_sequence:
    image "bg shelter.png"
    imagebutton auto "pot-%s.png" action [Play("sound", "audio/click.mp3"), Hide("Cooking_sequence"), Show("food_puzzle")] at food_transform


# define characters
define c = Character('', what_prefix='"', what_suffix='"', what_color="#ffb351") # canary
define m = Character('', what_prefix='"', what_suffix='"', what_color="#669292") # maria
define n = Character('', what_prefix='{i}', what_suffix='{/i}', what_color="#669292") # narrator
define r = Character('', what_prefix='<', what_suffix='>', what_color="#964B00") # radio
define t = Character('', what_prefix='<', what_suffix='>', what_color='#c14949') # TV

# define images
image radio = Image("radio.png", xalign=0.5, yalign=0.3)
image burnt = Image("burnt.png", xalign=0.5, yalign=0.3)

python early:
    def sprite_visible():
        return renpy.showing("canary") or renpy.showing("maria")

screen displayTextScreen(displayText):
    frame:
        xalign 0.5
        yalign 0.8

        text displayText

label start:

    # Sprites
    $ slider_SM = SpriteManager(update = slider_update)
    $ slider_sprites = []

    # Safe zone variables
    $ safe_zone_image = Image("safe-zone.png")
    $ safe_zone_transform = Transform(child = safe_zone_image, zoom = 0.5)
    $ safe_zone_size = (int(149/2), int(70/2))
    $ slider_sprites.append(slider_SM.create(safe_zone_transform))
    $ slider_sprites [-1].type = "safe-zone"

    # Slider variables
    $ slider_bar_size = (int(545/2), int(70/2))
    $ slider_image = Image("slider.png")
    $ slider_transform = Transform(child = slider_image, zoom = 0.5)
    $ slider_sprites.append(slider_SM.create(slider_transform))
    $ slider_sprites [-1].type = "slider"
    $ slider_sprites [-1].direction = "right"
    $ slider_size = (int(48/2), int(66/2))
    $ slider_speed = 2
    $ stop_slider = False

    # Food variabes
    $ food_cooked = False
    $ food_cooked_tries = 1
    $ food_difficulty = 2

    # Set default volume
    define config.default_music_volume = 0.4
    define config.default_sfx_volume = 0.7
    define config.default_voice_volume = 0.7

    jump Prologue

    label Prologue:
        scene bg bedroom
        with fade

        play music "birdsong.mp3"

        n "I have a bad habit of waking up and immediately feeling anxious about something."
        n "This morning, I can't figure out what it is."
        n "I just lie there, staring at the ceiling, listening to our bird sing."
        n "{i}*yawn*{/i}"
        
        m "...It's too early..."

        show canary smug  

        c "Good morning to you too~!"

        hide canary
        show maria annoyed

        m "Canary." 
        m "It's six in the morning..."

        hide maria
        show canary frown

        c "I think you'll find it's six {i}thirty{/i}, actually!"

        show canary smug

        c "And because I'm so thoughtful, I've already made breakfast."
        c "Since you're such a sleepyhead~"

        show canary grin

        c "So you're welcome!"

        hide canary 
        show maria neut 

        m "I didn't ask you to..."

        hide maria
        show canary frown

        c "No, but your stomach did."

        show canary smug

        c "I could hear it asking all the way from my room~!"

        hide canary
        show maria annoyed

        m "That is a complete lie."

        hide maria
        show canary smug

        c "Ahh, truth, lie - whatever!"

        show canary grin

        c "Just come and eat before it gets cold!"

        hide canary

        n "I watch as she retreats back to the kitchen."
        n "She's humming something to herself. That makes for 2 birds singing at way-too-early o'clock."
        n "I stare at the ceiling for another few seconds."
        n "Should I tell her that I appreciate her? I sure as hell don't tell her enough."
        n "I don't tell her a lot of things that I should."
        n "...I'm thinking about this too hard. It's six thirty."

        show maria neut

        menu:
            m "I'll just..."
            "Tell her.":
                jump Maria_is_brave
            
            "Don't.":
                jump Maria_is_shy

    label Maria_is_shy:
        hide maria

        n "I clear my throat to call out to Canary."

        show maria pout

        m "I'm not a sleepyhead, by the way!!"

        show maria neut 

        m "I just... I just like sleeping in a lot, that's all!"

        hide maria
        show canary smug

        c "Sure, sure."
        c "Whatever makes you feel better~"
        c "Just get over here already!"

        hide canary
        show maria annoyed

        m "I'm coming, I'm coming..."

        scene bg kitchen

        jump Look_at_the_bird

    label Maria_is_brave:
        hide maria

        n "I pull myself out of bed and into our modest kitchen."

        scene bg kitchen

        show maria smile

        m "Hey, Canary."

        hide maria
        show canary neut

        c "Hmm~?"

        hide canary
        show maria smile

        m "Thank you. For breakfast. And... I don't know."
        m "Just. In general."

        hide maria
        show canary tilt

        c "...are you being sincere right now?"
        c "At six thirty in the morning?"

        hide canary
        show maria pout

        m "Nevermind, just forget it-"

        hide maria
        show canary grin

        c "No, no, I'm liking this energy! That's the cutest thing I've ever heard you say!"

        show canary neut

        c "I'm receiving it. I'm receiving the sincerity."
        c "I can be sincere too!"

        show canary frown

        c "Hang on, let me get ready."

        hide canary
        show maria pout

        m "Canary-"

        hide maria
        show canary neut

        c "Okay. Ready."

        show canary soft

        c "Maria. My dearest, most dramatic, most anxious, least-morning-person best friend..."

        show canary grin

        c "I appreciate you to the world and back, forever and ever and ever~!"

        hide canary
        show maria smile

        m "Don't make it weird, you weirdo."
        m "It's just..."
        m "We've been together since we were kids."
        m "I just think about that, sometimes."
        m "I... can't imagine a version of my life where you aren't in it."

        show maria neut

        n "...That was mortifying."

        hide maria
        show canary tilt

        c "..."

        show canary soft

        c "Don't you worry."

        show canary grin

        c "You're stuck with me forever, like it or not~!"

        jump Look_at_the_bird

    label Look_at_the_bird:
        hide canary
        hide maria

        n "We finish breakfast together."
        n "Canary's toast and eggs are fine. They aren't particularly GOOD..."
        n "She definitely isn't the best cook in the world, but." 
        n "It's the thought that counts."

        n "While Canary is busy doing the dishes, I grab our bag of birdseed and go to greet our pet bird."
        n "She's been singing since before I woke up, like some kind of alarm clock."

        show maria smile

        m "Good morning, pretty bird."

        hide maria

        n "The bird tilts her head at me, looking at me with her big, round eyes."

        show canary smug

        c "She likes you, you know!"

        hide canary
        show maria neut

        m "She likes whoever feeds her."

        hide maria
        show canary soft

        c "She likes you the most."

        hide canary

        n "...I'm not sure why I find that so hard to believe."

        # metaphor for canary liking maria but maria never realising it
        # alt: n "She's staring at me like I'm the most interesting thing in the world."
        # n "I probably am, to her. I'm the one with the seeds."

        jump start_birdminigame
    
    style stat_bar: 
        left_bar Frame ("#ff9305" )
        right_bar Frame ("#fffb05")

    transform small: 
        zoom 0.35

    transform bird: 
        pos(1035, 170)

    transform centre: 
        pos(900, 50)
        zoom 0.5

    label start_birdminigame:
        show screen my_screen
        show screen stat_buttons

        "Click on the buttons or drag the bars to care for your bird"

        $ renpy.pause (hard= True)
        
    screen my_screen:
        add "bedroom.jpg"

    screen stat_buttons:
        fixed:
            # Shared midpoint
            $ mid_x = 1400
            $ y = 150

            # Bird frames
            if frame_num == 0:
                add "bird1.png" xpos mid_x - 60 ypos y + 110
            elif frame_num == 1:
                add "bird2.png" xpos mid_x - 60 ypos y + 110
            elif frame_num == 2:
                add "bird3.png" xpos mid_x - 60 ypos y + 110
            elif frame_num == 3:
                add "bird4.png" xpos mid_x - 60 ypos y + 110

            # Cage
            add "birdcage.png" xpos mid_x + 30 ypos y

        frame: 
            background "#ff9305" 
            pos(350,100)
            xsize 150
            ysize 75
            text "Hunger"

        frame: 
            background "#ff9305" 
            pos(350,250)
            xsize 150
            ysize 75
            text " Thirst"

        frame: 
            background "#ff9305" 
            pos(350,400)
            xsize 150
            ysize 75
            text "   Joy"
        
        bar value VariableValue("hunger", range= 15): 
            style "stat_bar"
            pos (550, 100)
            xsize 500
            ysize 75 

        bar value VariableValue("thirst", range= 15):
            style "stat_bar"
            pos (550, 250) 
            xsize 500
            ysize 75

        bar value VariableValue("happiness", range= 15): 
            style "stat_bar"
            pos (550, 400)
            xsize 500
            ysize 75

        timer 0.1 repeat True action If(hunger + thirst + happiness >= 37, Jump("Siren_goes_off") )

        imagebutton:
            idle "bone.png" at small 
            action [Play("sound", "audio/click.mp3"), SetVariable("hunger", hunger + 1), SetVariable("frame_num", (frame_num+1) % 4)]
            pos (300, 500)

        imagebutton:
            idle "thirst.png" at small 
            pos (550, 500) 
            action [Play("sound", "audio/click.mp3"), SetVariable("thirst", thirst + 1), SetVariable("frame_num", (frame_num+1) % 4)]

        imagebutton:
            idle "happyface.png" at small 
            pos (800, 500) 
            action [Play("sound", "audio/click.mp3"), SetVariable("happiness", happiness + 0.5), SetVariable("frame_num", (frame_num+1) % 4)]

    label Siren_goes_off:
        play music "siren.mp3"
        hide screen stat_buttons with fade 
        hide screen my_screen with fade

        show maria shock

        m "!!!"

        hide maria
        
        n "It's from the living room."
        n "Another siren test, maybe. They've been doing those a lot lately."

        c "Hey, Maria? Can you..."
        c "Can you come here?"

        n "Her voice is... different."
        n "I go to the living room."

        show maria pout

        m "What's going on?"

        hide maria
        scene bg alert
        show canary frown

        c "It's..."
        # famous last words from real!canary

        hide canary

        t "ATTENTION. ATTENTION."
        t "A NUCLEAR ATTACK HAS BEEN CONFIRMED. CITIZENS ARE ADVISED TO SEEK SHELTER IMMEDIATELY."
        t "THIS IS NOT A DRILL. REPEAT, THIS IS NOT A DRILL."
        t "ATTENTION. ATTENTION."
        t "A NUCLEAR ATTACK HAS BEEN CONFIRMED. CITIZENS ARE ADVISED TO SEEK SHELTER IMMEDIATELY."
        #  t "THIS IS NOT A DRILL. REPEAT, THIS IS NOT A DRILL."
        # screen record the above line, then add it to the start of the intro.webm to interrupt it with static

        $ renpy.movie_cutscene("images/intro.webm")

        stop music
        scene bg black
        with fade

        jump Main_game

    label Main_game:
        c "--aria--!"
        c "Wake up, Maria!"

        scene bg wake1
        with fade
        play music "yellow-bells.wav"
        # cg of canary peering down at maria, frown

        c "Maria?"

        n "My head hurts."
        n "The air smells like concrete and must and something burning."
        n "I blink up at her."

        scene bg wake2
        # same but with smile of relief

        c "Oh, you're awake."
        c "Thank god, I thought you were a goner for a second there!"

        scene bg shelter
        show maria shock
        # subconscious: CANARY ALIVE??? BUT CANARY DEAD?????

        m "...Canary?"

        hide maria
        show canary smug

        c "In the flesh~!"

        hide canary
        show maria pout

        m "What... what happened? Where are we?"

        hide maria 
        show canary neut 

        c "Bomb shelter. You hit your head on the ladder on the way down."

        show canary smug

        c "Very graceful~"

        hide canary
        show maria pout

        m "Oh..."
        m "...How long has it been?"

        hide maria
        show canary frown

        c "A while. You sleepyhead."

        show canary smug 

        c "I, meanwhile, have been absolutely slaving away over here. Breaking my back, even!"

        show canary wsmile

        c "I got the fire going. Catalogued our supplies. Single-handedly kept us both alive, really."

        hide canary 
        show maria neut

        m "So heroic."

        hide maria
        show canary smug

        c "I know, right~?"

        hide canary
        show maria shock

        m "Wait, did you say you made a fire?"

        hide maria 
        show canary wopen 

        c "Yep! Relax, I vented it properly. Filters."
        c "Bad smoke goes out, good hot air stays in."

        show canary smug

        c "It's all very scientific."

        hide canary
        show maria neut

        m "Oh... okay. That's good."
        m "Thanks."

        show maria pout

        m "You're okay, right?"
        m "You didn't get hurt or anything?"

        hide maria 
        show canary wsmile

        c "Yep!"

        show canary grin

        c "Don't worry about me, you worrywart~"

        show canary wsmile
        c "I already ate all of my share of rations while you were taking a nap--"

        hide canary
        show maria annoyed

        m "--Not a nap--"

        hide maria
        show canary smug

        c "--so you'd better get started on your portion!"

        show canary neut

        c "I'd offer to cook it for you, but-"

        hide canary
        show maria shock

        m "No, no, I can do it!"

        show maria smile

        n "Sorry, but there's only so much of Canary's cooking I can take in one day..."

        hide maria
        show canary frown

        c "I can tell what you're thinking, y'know."

        show canary wsmile

        c "I'm choosing not to take offense to that."

        hide canary

        n "She gestures towards the cupboards, where the rations presumably live."

        show canary wopen

        c "Go on!"

        hide canary

        stop music

        jump start_Cookingsequence

label start_Cookingsequence:
    scene bg shelter
    window hide

    # variables
    $ draggable = ""
    $ droppable = ""
    $ bag = 0
    $ tomato = 0
    $ basil = 0

    call foodstore
    call foodMiniVAr

    return

label foodMiniVAr:
    while True:
        $ result = renpy.call_screen("setDragImages")

        if result == "start":
            jump Cooking_sequence

        if draggable == "bag":
            $ bag -= 1
        elif draggable == "tomato":
            $ tomato -= 1
        elif draggable == "basil":
            $ basil -= 1

        $ draggable = ""

label foodstore: 
    # a python mini pantry! 

    $ bag = 2
    $ tomato = 5
    $ basil = 8

    return

screen setDragImages: 
    "Drag the food of your choice into the saucepan, be careful not to use all the rations!"
    
    textbutton "Start Cooking!":
        text_color "#ff0000"
        pos (1500, 750)
        action Return("start")
    
    # can add other elements to image, i.e. add a table = add "bg table.png"

    # contents of the saucepan
    text "Available rations:":
        pos (1500, 550) 
        bold True
        color "#ffffff" 

    text "Bag = [bag]": 
        pos (1500, 600) 
        bold True
        color "#ffffff"    
    
    text "Canned Tomato = [tomato]": 
        pos (1500, 650) 
        bold True
        color "#ffffff" 
    
    text "Basil = [basil]": 
        pos (1500, 700) 
        bold True
        color "#ffffff"
    
    draggroup :
        drag:
            drag_name "saucepan"
            xpos 650
            ypos 500
            child "saucepan.png"
            draggable False 
            droppable True 
        
        drag: 
            drag_name "bag"
            xpos 225
            ypos 375
            child im.Scale("bag-of-pasta.png", 400, 400)
            draggable (bag > 0)
            droppable False 
            dragged drag_placed
            drag_raise True # when clicked, photo is on the top layer

        drag: 
            drag_name "tomato"
            xpos 1200
            ypos 400
            child im.Scale("tomato.png", 200, 300)
            draggable (tomato > 0)
            droppable False 
            dragged drag_placed
            drag_raise True # when clicked, photo is on the top layer

        drag: 
            drag_name "basil"
            xpos 775
            ypos 150
            child im.Scale("basil.png", 300, 200)
            draggable (basil > 0)
            droppable False 
            dragged drag_placed
            drag_raise True # when clicked, photo is on the top layer 

label Cooking_sequence:
    call screen Cooking_sequence

label Sucessful_cooking:
    hide screen food_puzzle
    scene bg shelter
    play music "yellow-bells.wav"
    show maria shock 

    m "That's..."

    show maria smile

    m "Not bad, actually!"

    show maria neut

    m "For war rations, anyway. Could be worse."

    hide maria 

    n "I eat slowly. The food is a little bland, but it's warm and it's filling."
    n "Canary has disappeared somewhere in the shelter."
    n "It's quiet without her."
    n "I try not to think much of it."
    n "{i}*yawn*{/i}"
    n "All that worrying got me pretty exhausted"
    n "I'll get some rest"

    stop music

    scene bg black

    jump Fan_sequence

label Failed_cooking:
    hide screen game_over
    hide screen food_puzzle
    scene bg shelter
    play music "yellow-bells.wav"
    show maria shock
    show burnt

    m "..."
    m "Ah."

    show maria pout

    m "That's. Not great."

    hide maria

    c "I leave you alone for {i}five minutes-{/i}"

    show maria shock

    m "What the--"

    hide maria
    show canary frown

    c "What happened?"

    hide canary
    show maria pout

    m "Er... the food..." 
    m "I kind of..."
    m "Cremated it a little."

    hide maria 
    show canary frown 

    c "You cremated your dinner."

    hide canary 
    show maria annoyed 

    m "Only a little!"

    hide maria
    show canary frown

    c "It's completely inedible!"

    show canary smug

    c "And you always said {i}I{/i} was the bad cook! HA!"

    hide canary
    hide burnt
    show maria pout

    m "I never say that..."

    hide maria
    show canary smug

    c "Oh, please. You very heavily implied it last Tuesday."

    show canary neut

    c "And Monday."

    show canary frown

    c "And... Um... Well, whatever."

    show canary wopen

    c "Don't you worry. You can just have my snacks!"

    hide canary
    show maria neut

    m "Wait, didn't you say you already ate your rations?"

    hide maria 
    show canary wopen 

    c "No, silly - I only ate a {i}portion{/i} of my rations."

    show canary smug

    c "I still had some saved for later, but I {i}guess{/i} I can give them to you."

    show canary grin

    c "Consider it payment for the entertainment~!"

    hide canary 
    show maria pout

    m "I hate you."
        
    hide maria
    show canary smug

    c "You really are useless without me, huh?"
    c "Just take them already!"

    hide canary 
    with fade

    n "I eat her snacks. They're actually pretty good, but they taste like defeat." 
    n "Canary's flitting around the tiny room. Apparently bomb shelter supplies are interesting to her."
    n "I glance at the pantry."
    n "Strange. It seems... fuller than it should be."
    n "She said she already ate. So why does it look like nothing's been touched?"

    show canary neut

    c "I'm gonna get some rest for a bit. You should too."
        
    hide canary

    n "I watch her go."
    n "Then I look back at the pantry."

    menu:
        n "...Should I ration out the food between us?"
        "Yes.":
            jump FOR_POORER_FOR_RICHER

        "No.":
            n "I'm probably just overthinking it."
            n "I close the pantry and don't think about it again."
            n "...I {i}TRY{/i} not to think about it again."
            n "Instead, I settle down in bed next to Canary - our one flat tiny bed - and go to sleep."

            stop music
            scene bg black

            jump Fan_sequence

label FOR_POORER_FOR_RICHER:

    n "That's right. I need to make sure Canary eats properly."
    n "I divide everything carefully. Half for me. Half for Canary."
    n "She's lying in bed. Probably asleep."
    n "I set her share aside in the corner so it's easy to find."
    n "That's the sensible thing to do."

    # Time passes in the bunker
    # Supplies are dwindling
    # shown by drawings of dwindling supplies
    # anary's rations go uneaten in a pile in the corner
    # When Maira is about to starve to death, she finally sees the pile of food

    #scene bg fpfr1
    #with fade
    # time indicated by calendar crossed out dates, pantry shelves running empty. 
    # fpfr1 is full, fpfr2 is medium, etc

    n "Days pass."
    n "Or - we think they do. It's hard to tell down here."

    #scene bg fpfr2
    #with fade

    n "I keep eating my half. I leave Canary's half."
    n "I tell myself that she's been eating her share when I'm not looking."

    #scene bg fpfr3
    #with fade

    n "She must have."
    n "She has to."

    scene bg shelter
    with fade

    n "And then one morning I wake up, and I'm so hungry I can barely sit up straight."
    n "I look in the corner."
    n "And I see it."
    n "Canary's share."

    show maria pout

    m "..."
    m "She..."
    m "Hasn't eaten any of it."

    show maria neut

    m "But..."

    show maria smile

    m "It's for Canary."
    m "I set it aside for her."
    m "She has to eat it."
    m "She..."
    m "She has to live."
    m "I need her to live."

    hide maria

    scene bg black
    with fade

    ".:. ENDING 2: FOR RICHER, FOR POORER"

    jump ending

    label Fan_sequence:
        play sound "clang.mp3"

        "{i}CLANG!{/i}"

        scene bg shelter
        with fade
        play music "yellow-bells.wav"
        show maria shock

        m "What was that?!"

        hide maria

        n "I shoot up in bed."
        n "Canary is still sound asleep next to me."
        n "I shake her gently."

        show maria neut

        m "Canary? Did you hear that?"

        hide maria
        show canary frown

        c "Whah...?"
        c "'s probably just some... pipes... or whatever... Chill..."

        hide canary
        
        n "She turns over and goes back to sleep."

        show maria shock

        m "That did {i}NOT{/i} sound like pipes or whatever!"

        show maria pout 
        
        m "...Maybe I {i}SHOULD{/i} chill."
        hide maria
        
        menu:
            n "But what if..?"
            "Investigate the noise.":
                jump Investigate_noise

            "Go back to sleep.":
                jump IN_SICKNESS_AND_IN_HEALTH

    label IN_SICKNESS_AND_IN_HEALTH:
        n "I lie back down."
        n "My head is pounding. It won't stop pounding."
        n "How long has it been pounding?"
        n "I turn over."

        scene bg isaih1
        with fade
        # cg of canary lying in bed, sleepy eyes.. dead wife flashback pose

        c "Don't worry, Maria."
        c "We'll be together forever and ever."

        scene bg isaih2
        # cg now glitchy/fuzzy/WRONG 

        c "Not even death can come between us."

        n "I don't understand..."
        n "I want to say something back."
        n "I can't remember what."
        n "It's getting hard to breathe."
        n "Everything... hurts..."

        scene bg black
        with fade
        
        ".:. ENDING 3: IN SICKNESS AND IN HEALTH"

        jump ending

    label Investigate_noise:
        show maria pout

        m "I need to check what that was."

        hide maria

        n "I clamber out of bed and... pretty much immediately spot the problem."

        scene bg ventclose
        show maria annoyed

        m "This vent is definitely broken..."
        m "Looks like it's been broken for a while, actually."

        show maria pout
        
        m "Argh, what do I do?!"
        m "Maybe we have a book that can help me fix it?"
        
        hide maria
        stop music

        jump Choose_Book

    label Choose_Book:
        call screen book_minigame

    screen book_minigame:
        "Choose a book"
        imagebutton:
            xanchor 0.5
            yanchor 0.5
            xpos 0.70
            ypos 0.5
            idle "DIY_idle.png"
            hover "DIY_hover.png"
            action [Play("sound", "audio/click.mp3"), Hide("displayTextScreen"), Jump("DIY_book")]
            hovered Show("displayTextScreen", displayText = "DIY Book")
            unhovered Hide("displayTextScreen")

        imagebutton:
            xanchor 0.5
            yanchor 0.5
            xpos 0.30
            ypos 0.5
            idle "medicine_idle.png"
            hover "medicine_hover.png"
            action [Play("sound", "audio/click.mp3"), Hide("displayTextScreen"), Jump("medicine_book")]
            hovered Show("displayTextScreen", displayText = "Medicine Book")
            unhovered Hide("displayTextScreen")

    label medicine_book:
        "Carbon Monoxide Poisoning."
        "Carbon monoxide is a colourless, odourless gas that can be deadly when inhaled in large amounts"
        "Symptoms include confusion, headaches, fatigue, disorientation."
        "In enclosed spaces with poor ventilation--"

        show maria pout 

        m "...hm."
        m "I don't think this is what I need."

        hide maria

        jump Choose_Book

    label DIY_book:
        show maria smile 

        m "There we go. This could work!"

        hide maria 
        
        scene bg ventopen
        with fade

        call screen vent_minigame

    screen vent_minigame:
        imagebutton:
            xanchor 0.5
            yanchor 0.5
            xpos 0.5
            ypos 0.5
            idle "feather_idle.png"
            hover "feather_hover.png"

            action [Play("sound", "audio/click.mp3"), Jump ("Maria_has_fixed_the_vent")]

    label Maria_has_fixed_the_vent:
        scene bg ventclose
        play music "yellow-bells.wav"
        show maria smile

        m "Yes! Done!"

        hide maria
        scene bg shelter
        with fade

        n "I sit back and feel disproportionately proud of myself."
        n "We're in a nuclear bunker and I fixed a vent. I basically saved the world."
        n "Well. {i}OUR{/i} world, at least..."
 
        show canary smug

        c "Hey, look at you~" 

        hide canary 
        show maria shock

        m "Wha- Were you watching this entire time?!" 

        hide maria
        show canary wsmile

        c "Just the end. Your proud face was very cute."

        hide canary
        show maria pout

        m "S-Shut up..."

        hide maria
        show canary grin

        c "I'm only teasing~!"

        hide canary

        n "This is surprisingly nice." 
        n "Canary riling me up, me getting flustered."
        n "Just like always..."
        n "I can almost forget about... this whole situation."
        n "But the problem of the rations is still bothering me."
        n "Surely Canary is starting to feel at least a little hungry... Should I..?"
        n "No, I shouldn't say anything. Just--"

        show canary tilt

        c "What's with the long face?"

        hide canary
        show maria shock

        m "Ack!"
        m "It's, um. It's nothing."

        hide maria
        show canary neut

        c "You don't have to lie to me, Maria."

        show canary smug

        c "Like. You're literally {i}incapable{/i} of lying to me."

        hide canary

        n "She's always been able to see straight through me."
        n "But I really don't want to press her about the rations--"

        show canary neut

        c "You're thinking about our bird, aren't you?"

        hide canary
        show maria neut

        m "..?"
        m "Oh... Y-Yeah. Our bird."

        hide maria

        n "That's... Actually..."
        n "I've been trying not to think about it. Because once I start thinking about it..."

        show maria pout

        m "Our bird."
        m "She..."
        m "She didn't make it, did she?"

        hide maria
        show canary neut

        c "..."
        c "Try not to be too upset, Maria."

        hide canary
        show maria pout

        m "I know, it's just..."

        n "{i}*sniffle*{/i}"

        show maria sad

        m "She was so small."
        m "And I- I keep thinking about her singing."
        m "She was ours, Canary, and I-"
        m "I should have done more. I should have gone back and-"

        hide maria
        show canary neut

        c "Hey, no, no, don't say that."

        show canary frown

        c "If either of us had run back for her, we wouldn't have made it to the shelter."

        show canary wsmile

        c "Not even you, with your absurdly long legs."

        hide canary
        show maria pout

        m "They're not {i}absurd{/i}..."

        hide maria
        show canary frown

        c "And then we'd all be dead, all three of us."
        c "What would the point of {i}that{/i} be?"

        hide canary 
        show maria sad

        m "I... guess you're right..."
        m "I just don't want to lose you too."
        m "I - I don't know what I'd do."

        hide maria
        show canary soft

        c "..."
        c "I'm upset she didn't make it."
        c "But... I'm not upset with how things turned out."
        c "And I'm definitely not upset with you."

        show canary wsmile

        c "You made it. That's what matters."

        hide canary
        show maria neut

        m "Yeah... We both made it."

        hide maria 
        scene bg ghosthug
        with fade

        n "Her arms trail down my back as we hug, like always."
        n "She squeezes me ever so slightly"
        n "But the warm rays of comfort that should seep from her presence don't reach me."
        n "She feels... cold."
    
        c "You're pretty warm, Maria."
        c "Maybe that fall did more than you care to admit!"

        n "As Canary slowly returns from the hug, her eyes drift to my hands."
        n "They're pale, clenched, shaking...."
        n "... Maybe the room's just gotten colder."
        n "I can't say anything."

        scene bg shelter
        show canary frown

        c "Hellooo~?"
        c "...Nothing? Not even a grumble?" 
        c "..."

        show canary neut

        c "I think the shock is finally getting to you."
        c "Get some rest, okay?"

        show canary wsmile

        c "I'll be right here when you wake up."

        hide canary
        with fade
        stop music

        jump Nightmare

    label Nightmare:
        scene bg black

        play music "creepy.mp3" fadein 1.0

        r "a-- lis-- any-- a-"

        c "Maria. Maria, wake up."
        c "Wake up."

        n "Something is wrong."

        scene bg black
        with fade
        # the ceiling?

        c "Look at me."

        # canary sitting on the bed facing away from camera:
        scene bg nightmare1
        show maria shock 
        with fade

        m "..."

        hide maria  

        c "...That stupid bird."

        show maria pout 

        m "Huh...?"
        m "Are we really talking about this again? I know--"

        hide maria 

        c "She was so small." 
        c "So small."
        c "Can you still hear her singing?"

        show maria shock 

        m "I... What...?"

        hide maria

        c "She's still up there. In a way."
        c "Such a small body."

        scene bg nightmare2
        # same as nightmare2 but head turned slightly towards us
        c "But what's the point, right?"
        # Repeating what canary already said about "what's the point if we're all dead"

        # hide canary 
        show maria pout

        m "I just... she was ours. Our bird. I'm allowed to..."

        hide maria 
        #show canary wrong 

        c "What colour were her eyes, Maria?"

        # hide canary

        menu:
            n "..."
            "BLACK":
                jump Wrong
            "BLUE":
                jump Wrong
            "BROWN":
                jump Wrong
            "RED":
                jump Wrong
            "GREEN":
                jump Wrong
            "YELLOW":
                jump Wrong

    label Wrong:
        scene bg nightmare3
        # the scary!

        c "You Don't Remember What She Looks Like"

        # hide canary 
        show maria sad

        #tears start to flow

        m "..."

        hide maria
        scene bg black
        # CG switches to Maria's hands in her lap, blurry (as if through Maria's eyes), teardrops on them

        c "Look at me. Why won't you look at me?"
        c "Do you hear that?"

        play music "creepy.mp3" volume 1.0

        c "L   i   s   t   e   n"

        stop music
        hide canary 

        jump Radio_sequence

    label Radio_sequence:
        scene bg black
        with fade
        play music static loop

        r "--h--he--"

        n "It's the sound of the radio."
        n "I turn over and try to go back to sleep."

        r "--ello---"
        r "---a- a-any...b--ody there?-------------"

        scene bg shelter
        show canary frown
        show radio
        with fade

        n "I sit up."
        n "Canary is standing over the radio with her back towards me."
        n "Her shoulders are tense."

        show canary tilt 

        c "Oh, you're awake."

        show canary wsmile

        c "I was just talking to myself. Don't mind me~!"

        hide canary 
        show maria pout 

        m "...Wasn't that the radio?"

        hide maria 
        show canary neut 

        c "Oh, that old thing? Hmm, well..."

        show canary tilt

        c "It keeps picking up weird interference." 

        show canary wopen

        c "Nothing useful. I wouldn't worry about it~!"

        hide canary 
        show maria pout 

        m "But I heard someone... It sounded like..."

        r "--I'm ---- at ----ear me?"

        show maria shock 

        m "There! That! Did you hear that?!"

        hide maria 
        show canary frown 

        c "It's just a stray signal from whatever's left of the local radio station."

        show canary wopen

        c "It's been playing on and off the whole time. Surely you've noticed~!"

        hide canary
        hide radio

        n "She sounds so certain. I want to believe her."

        stop music

        menu:
            n "Do I believe her?"
            "Yes":
                jump TILL_DEATH_DO_US_PART

            "No":
                jump Maria_disbelieves_Canary

    label TILL_DEATH_DO_US_PART:
        play music "yellow-bells.wav"
        show maria neut

        m "I... guess you're right."

        hide maria 
        show canary smug 

        c "Still half-asleep, huh~?"

        show canary wsmile

        c "Come on. Don't waste your energy on that thing."

        hide canary
        hide bg shelter
        with fade

        #Cutscne 4: Time passes in the bunker
        #Shown by drawings of supplies dwindling or Maria sitting at a table with Canary, who over snapshots of time, remains the same while Maria deteriorates

        scene bg tddup1
        with fade
        # maria and canary sitting at the bunker table

        n "I stop listening for the radio."

        scene bg tddup2
        # same pose, same table - canary looks exact same, maria looks more gaunt + tired. supplies in bg dwindling

        n "I stop counting the days, after a while."

        scene bg tddup3
        # same gimmick, maria looks Very Rough now... verge of death-ish
        # the final conversation

        n "I stop thinking about a lot of things."

        c "Maria..."
        c "You couldn't let me go."

        m "..."

        c "You should've moved on."
        c "Met new people."
        c "Forgotten about me."
        c "But instead you stayed here."
        c "Just the two of us."
        c "You made yourself dependent on me."
        c "My comfort."

        m "..."

        c "You could still leave, you know."
        c "But I guess you have no energy left, right?"

        m "..."

        c "You really don't want to live without me, do you."

        m "..."

        scene bg black
        with fade

        c "Then..."
        c "Will you join me?"

        ".:. ENDING 5: TILL DEATH DO US PART"

        jump ending

    label Maria_disbelieves_Canary:
        play music "yellow-bells.wav"

        n "No way. I definitely heard someone talking."
        n "But... I can't disagree with her to her face..."
        n "Just like always."

        show maria smile 

        m "Ahaha.. Yeah. Yeah, you're right."

        show maria neut
        m "I think I'll stay up a bit longer, though."
        m "Not really tired anymore."

        hide maria 
        show canary neut

        c "Oh, Maria..."
        c "You've always been such a worrywart."
        c "You don't need to stress."

        show canary wsmile 

        c "You have me, after all."

        stop music
        hide canary 
        show radio
        play music static loop

        r "--h--hello? Is anyone out there?"
        r "I've got the signal working. I don't know how long it'll hold..."
        r "If you can hear this, make your way to the town square. We're organising an evacuation."
        r "There are other survivors here."
        r "Please. If anyone can hea--a--this----"

        show maria shock 

        m "Canary!"
        m "Did you hear {i}that?!{/i}"
        m "That was a person. A real person."

        hide maria 
        show canary neut 

        c "Ah."

        show canary wsmile

        c "I... yes, but..." 

        show canary frown

        c "How do we know it's not a trap?"

        show canary neut

        c "Aren't you scared?"
        c "We're safer here. Together."

        hide canary 

        n "Something is wrong."
        n "The Canary I know has never been afraid of anything in her life."
        n "She'd sprint towards the exit the moment she heard the word 'evacuation'."
        n "Drag me along by the wrist if she had to."
        n "Why is she telling me to stay?"

        show maria pout 

        m "There are other people out there. We have to go."
        m "Our supplies won't last forever, and..."

        hide maria

        n "...There's no point in being together if we're both dead."

        show canary tilt 

        c "But… what if it's dangerous?"

        show canary neut

        c "We have everything we need here." 
        c "Just the two of us. Isn't that enough?"

        show canary tilt

        c "We said we'd be together forever and ever~"

        show canary wsmile

        c "Didn't you mean it?"

        hide radio 
        hide canary
        stop music

        menu:
            n "Make the choice."
            "Stay.":
                jump FOR_BETTER_OR_FOR_WORSE

            "Leave.":
                jump TO_LOVE_AND_TO_CHERISH

    label FOR_BETTER_OR_FOR_WORSE:
        play music "yellow-bells.wav"

        n "That's right."
        n "I've never been able to say no to her."

        show maria neut

        m "Ha..."

        show maria smile

        m "Haha. Hahaha...!"

        show maria pout

        m "...Yeah. Yeah, okay."
        m "You're right. Of course you're right. We'll stay."

        hide maria
        show canary neut

        c "..."

        hide canary
        show maria smile

        m "It's funny."
        m "I can see it now."
        m "I can see exactly what's happening."

        m "You..."

        scene bg flashback1
        # canary running back

        m "You went back for the bird."
        m "You went back, and you didn't--"

        scene bg flashback2
        # canary with the cage in her hands, far away, realising she's not gonna make it
        show maria sad

        m "You couldn't--"

        scene bg shelter
        show maria pout 

        m "..."
        m "I've known. For a while now, I think."
        m "Somewhere underneath it all."

        show maria sad

        m "But if I say it out loud..."
        m "Then you're really..."

        hide maria
        show canary neut

        c "..."

        hide canary

        n "I can't kill her again."
        
        show maria smile

        m "...Silly me. Just forget about what I was saying."
        m "We'll stay."
        m "I'll stay with you, Canary."

        hide maria

        #Flashes of the final cutscene is shown

        scene bg black

        ".:. ENDING 1: FOR BETTER OR FOR WORSE?"

        jump ending

    label TO_LOVE_AND_TO_CHERISH:
        play music "yellow-dove.wav"

        n "She's scared."
        n "She's never been scared."
        n "That's always been my job."
        
        scene bg flashback1
        n "The Canary I know laughs too loud in libraries, "
        n "and pets every stray animal she finds,"

        scene bg flashback2
        n "and never once in her life worried about being safe or careful."

        scene bg flashback3
        # closeup of canary's face as the blast approaches, soft teary smile. an "i'm sorry" or "it's okay" smile
        m "She runs towards things."
        m "She wouldn't tell me to stay."

        scene bg shelter
        show maria neut

        m "I'm going."
        m "You can stay here if you want."
        m "I'll come back if it's safe."
        m "...I'll come back for you."

        hide maria

        n "I know I won't."

        show canary neut

        n "She knows I won't."

        hide canary

        n "I think that's why she doesn't reach out to stop me. She can't."
        n "We both know she can't."
        n "I pick up my bag and walk towards the bunker door."
        n "My legs feel strange. Too heavy."
        n "One foot in front of the other."
        n "I don't look at her. If I look at her, I fear I won't leave."
        n "I place my hand on the door handle."

        show canary soft 

        c "Goodbye, Maria." # Fake!Canary's last words

        hide canary
        scene bg ruins
        with fade

        n "Sunlight pierces my eyes, grey rubble as far as I can see."
        n "The world, cracked open and quiet."
        n "The bunker door is still open, but..."

        # cg of doorway, maria casting a shadow

        n "...There's nobody there."

        n "Canary is dead."
        n "I knew."
        n "I've known for a while."
        n "I just needed a little longer."
        n "...I think she understood that."
        n "In the distance: the town square. Campsites. Survivors."
        n "A future that is strange and unknown and terrifying."
        n "I turn towards it."
        n "And I walk."

        ".:. TRUE ENDING (4): TO LOVE AND TO CHERISH"

        jump ending

    label ending:

    return
