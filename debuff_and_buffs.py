from ansi_tags import ansiprint

class EffectInterface():
    '''Responsible for applying effects, creating buff/debuff dictionaries, and counting down certain effects'''
    def __init__(self):
        # Effects that wear off at the start of your turn despite not being duration effects
        self.REMOVE_ON_TURN = ('Next Turn Block', 'Energized', 'Amplify', 'Burst', 'Double Tap', 'Duplication', 'Flame Barrier', 'Rebound', 'Simmering Rage',
                               'No Draw', 'Slow', 'Choked', 'Entangled')
        self.DURATION_EFFECTS = (
            "Frail", "Poison", "Vulnerable", "Weak", "Draw Reduction", 'Lock On', "No Block", "Intangible", "Blur", "Collect", 'Double Damage',
            "Equilibrium", "Phantasmal", "Regeneration", "Fading"
            )
        self.NON_STACKING_EFFECTS = (
            "Confused", "No Draw", "Entangled", "Barricade", "Back Attack", "Life Link", "Minion", "Reactive", "Shifting", "Split",
            "Stasis", "Unawakened", "Blasphemer", "Corruption", "Electro", "Master Reality", "Pen Nib", "Simmering Rage",
            "Surrounded"
            )
        self.PLAYER_BUFFS = {
            "Artifact": "Negate the next X debuffs",
            "Barricade": "<bold>Block</bold> is not removed at the start of your turn",
            "Buffer": "Prevent the next X times you would lose HP",
            "Dexterity": "Increases <bold>Block</bold> gained from cards by X",
            "Draw Card": "Draw X aditional cards next turn",
            "Draw Up": "Draw X additional cards each turn",
            "Energized": "Gain X additional <bold>Energy</bold> next turn",
            "Focus": "Increases the effectiveness of <bold>Orbs</bold> by X",
            "Intangible": "Reduce ALL damage and HP loss to 1 for X turns",
            "Mantra": "When you gain 10 Mantra, enter <bold>Divinity</bold>",
            "Metallicize": "At the end of your/its turn, gains X <bold>Block</bold>",
            "Next Turn Block": "Gain X <bold>Block</bold> next turn",
            "Plated Armor": "At the end of your/its turn, gain X <bold>Block</bold>. Recieving unblocked attack damage reduces Plated Armor by 1.",
            "Ritual": "At the end of your/its turn, gains X <bold>Strength</bold>",
            "Strength": "Increases attack damage by X",
            "Thorns": "When attacked, deal X damage back",
            "Vigor": "Your next Attack deals X additional damage",
            "Accuracy": "<bold>Shivs</bold> deal X additonal damage",
            "After Image": "Whenever you play a card, gain X <bold>Block</bold>",
            "Amplify": "Your next X Power cards are played twice",
            "Battle Hymn": "At the start of each turn, add X <bold>Smites</bold> into your hand",
            "Berzerk": "At the start of your turn, gain 1 <bold>Energy</bold>",
            "Blasphemer": "At the start of your turn, die",
            "Blur": "<bold>Block</bold> is not removed at the start of your next X turns.",
            "Brutality": "At the start of your turn, lose X HP and draw X card(s)",
            "Burst": "Your next X Skills are played twice",
            "Collect": "Put a <bold>Miracle+</bold> into your hand at the start of your next X turns",
            "Combust": "At the end of your turn, lose 1 HP for each <bold>Combust</bold> played and deal X damage to ALL enemies",
            "Corruption": "Skills cost 0. Whenever you play a Skill, <bold>Exhaust</bold> it",
            "Creative AI": "At the start of your turn, add X random <power>Power</power cards into your hand",
            "Dark Embrace": "Whenever a card is <bold>Exhausted</bold>, gain X <bold>Block</bold>",
            "Demon Form": "At the start of your turn, gain X <bold>Strength</bold>",
            "Deva": "At the start of your turn, gain X <bold>Energy</bold> N times and increase X by 1",
            "Devotion": "At the start of your turn, gain X <bold>Mantra</bold>",
            "Double Damage": "Attacks deal double damage for X turns",
            "Double Tap": "Your next X Attacks are played twice",
            "Duplication": "Your next X cards are played twice",
            "Echo Form": "The first X cards you play each turn are played twice",
            "Electro": "<bold>Lightning</bold> hits ALL enemies",
            "Envenom": "Whenever you deal unblocked attack damage, apply X <bold>Poison</bold>",
            "Equilibrium": "<bold>Retain</bold> your hand for X turns",
            "Establishment": "Whenever a card is <bold>Retained</bold>, reduce its cost by X",
            "Evolve": "Whenever you draw a Status card, draw X cards",
            "Feel No Pain": "Whenever a card is <bold>Exhausted</bold>, gain X <bold>Block</bold>",
            "Fire Breathing": "Whenever you draw a Status or Curse card, deal X damage to ALL enemies",
            "Flame Barrier": "When attacked, deals X damage back. Wears off at the start of your next turn",
            "Foresight": "At the start of your turn, <bold>Scry</bold> X",
            "Free Attack Power": "The next X Attacks you play cost 0",
            "Heatsink": "Whenever you play a Power card, draw X cards",
            "Hello": "At the start of your turn, add X random Common cards into your hand",
            "Infinite Blades": "At the start of your turn, add X <bold>Shivs</bold> into your hand",
            "Juggernaut": "Whenever you gain <bold>Block</bold>, deal X damage to a random enemy",
            "Like Water": "At the end of your turn, if you are in <bold>Calm</bold>, gain X <bold>Block</bold>",
            "Loop": "At the start of your turn, trigger the passive ablity of your next orb X times",
            "Machine Learning": "At the start of your turn, draw X additional cards",
            "Magnetism": "At the start of your turn, add X random colorless cards into your hand",
            "Master Reality": "Whenever a card is created during combat, <bold>Upgrade</bold> it",
            "Mayhem": "At the start of your turn, play the top X cards of your draw pile",
            "Mental Fortress": "Whenever you switch <bold>Stances</bold>, gain X <bold>Block</bold>",
            "Nightmare": "Add X of a chosen card into your hand next turn",
            "Nirvana": "Whenever you <bold>Scry</bold>, gain X <bold>Block</bold>",
            "Noxious Fumes": "At the start of your turn, apply X <bold>Poison</bold> to ALL enemies",
            "Omega": "At the end of your turn, deal X damage to ALL enemies",
            "Panache": "Whenever you play 5 cards in a single turn, deal X damage to ALL enemies",
            "Pen Nib": "Your next Attack deals double damage",
            "Phantasmal": "Deal double damage for the next X turns",
            "Rage": "Whenever you play an Attack, gain X <bold>Block</bold>. Wears off next turn",
            "Rebound": "The next X cards you play this turn are placed on top of your draw pile",
            "Regeneration": "At the end of your turn, heal X HP and decrease Regeneration by 1",
            "Rushdown": "Whenever you enter <bold>Wrath</bold>, draw X cards",
            "Repair": "At the end of combat, heal X HP",
            "Rupture": "Whenever you lose HP from a card, gain X <bold>Strength</bold>",
            "Sadistic": "Whenever you apply a debuff to an enemy, deal X damage to that enemy",
            "Simmering Rage": "Enter <bold>Wrath</bold> next turn",
            "Static Discharge": "Whenever you take unblocked attack damage, channel X <bold>Lightning</bold>",
            "Storm": "Whenever you play a Power card, channel X <bold>Lightning</bold>",
            "Study": "At the end of your turn, shuffle X <bold>Insights<bold> into your draw pile",
            "Surrounded": "Recieve 50% more damage when attacked from behind. Use targeting cards or potions to change your orientation",
            "The Bomb": "At the end of 3 turns, deal X damage to ALL enemies",
            "Thousand Cuts": "Whenever you play a card, deal X damage to ALL enemies",
            "Tools of the Trade": "At the start of your turn, draw X cards and discard X cards",
            "Wave of the Hand": "Whenever you gain <bold>Block</bold> this turn, apply X <bold>Weak</bold> to ALL enemies",
            "Well-laid Plans": "At the end of your turn, <bold>Retain</bold> up to X cards.",
        }
        self.PLAYER_DEBUFFS = {
            "Confused": "The costs of your cards are randomized on draw, from 0 to 3",
            "Dexterity Down": "At the end of your turn, lose X <bold>Dexterity</bold>",
            "Frail": "<bold>Block</bold> gained from cards is reduced by 25%",
            "No Draw": "You may not draw any more cards this turn",
            "Strength Down": "At the end of your turn, lose X <bold>Strength</bold>",
            "Vulnerable": "You/It takes 50% more damage from attacks",
            "Weak": "You/It deals 25% less damage from attacks",
            "Bias": "At the start of your turn, lose X <bold>Focus</bold>",
            "Contricted": "At the end of your turn, take X damage",
            "Draw Reduction": "Draw 1 less card the next X turns",
            "Entangled": "You may not play Attacks this turn",
            "Fasting": "Gain X less Energy at the start of each turn",
            "Hex": "Whenever you play a non-Attack card, shuffle X <bold>Dazed</bold> into your draw pile",
            "No Block": "You may not gain <bold>Block</bold> from cards for the next X turns",
            "Wraith Form": "At the start of your turn, lose X <bold>Dexterity</bold>"
        }
        self.ENEMY_BUFFS = {
            "Artifact": "Negate the next X debuffs",
            "Barricade": "<bold>Block</bold> is not removed at the start of your turn",
            "Intangible": "Reduce ALL damage and HP loss to 1 for X turns",
            "Metallicize": "At the end of your/its turn, gains X <bold>Block</bold>",
            "Plated Armor": "At the end of your/its turn, gain X <bold>Block</bold>. Recieving unblocked attack damage reduces Plated Armor by 1.",
            "Ritual": "At the end of your/its turn, gains X <bold>Strength</bold>",
            "Strength": "Increases attack damage by X",
            "Regen": "At the end of its turn, heals X HP",
            "Thorns": "When attacked, deal X damage back",
            "Angry": "Upon recieving attack damage, gains X <bold>Strength</bold>",
            "Back Attack": "Deals 50% increased damage as it is attacking you from behind",
            "Beat of Death": "Whenever you play a card, take X damage",
            "Curiosity": "Whenever you play a Power card, gains X <bold>Strength</bold>",
            "Curl Up": "On recieving attack damage, curls up and gains X <bold>Block</bold>(Once per combat)",
            "Enrage": "Whenever you play a Skill, gains X <bold>Strength</bold>",
            "Explosive": "Explodes in N turns, dealing X damage",
            "Fading": "Dies in X turns",
            "Invincible": "Can only lose X more HP this turn",
            "Life Link": "If other <bold>Darklings</bold> are still alive, revives in 2 turns",
            "Malleable": "On recieving attack damage, gains X <bold>Block</bold>. <bold>Block</bold> increases by 1 every time it's triggered. Resets to X at the start of your turn",
            "Minion": "Minions abandon combat without their leader",
            "Mode Shift": "After recieving X damage, changes to a defensive form",
            "Painful Stabs": "Whenever you recieve unblocked attack damage from this enemy, add X <bold>Wounds</bold> into your discard pile",
            "Reactive": "Upon recieving attack damage, changes its intent",
            "Sharp Hide": "Whenever you play an Attack, take X damage",
            "Shifting": "Upon losing HP, loses that much <bold>Strength</bold> until the end of its turn",
            "Split": "When its HP is at 50% or lower, splits into 2 smaller slimes with its current HP as their Max HP",
            "Spore Cloud": "On death, applies X <bold>Vulnerable</bold>",
            "Stasis": "On death, returns a stolen card to your hand",
            "Strength Up": "At the end of its turn, gains X <bold>Strength</bold>",
            "Thievery": "Steals X <yellow>Gold</yellow> when it attacks",
            "Time Warp": "Whenever you play N cards, ends your turn and gains X <bold>Strength</bold>",
            "Unawakened": "This enemy hasn't awakened yet...",
        }
        self.ENEMY_DEBUFFS = {
            "Poison": "At the beginning of its turn, loses X HP and loses 1 stack of Poison",
            "Shackled": "At the end of its turn, regains X <bold>Strength</bold>",
            "Slow": "The enemy recieves (X * 10)% more damage from attacks this turn. Whenever you play a card, increase Slow by 1",
            "Vulnerable": "You/It takes 50% more damage from attacks",
            "Weak": "You/It deals 25% less damage from attacks",
            "Block Return": "Whenever you attack this enemy, gain X <bold>Block</bold>",
            "Choked": "Whenever you play a card this turn, the targeted enemy loses X HP",
            "Corpse Explosion": "On death, deals X times its Max HP worth of damage to all other enemies",
            "Lock-On": "<bold>Lightning</bold> and <bold>Dark</bold> orbs deal 50% more damage to the targeted enemy",
            "Mark": "Whenever you play <bold>Pressure Points</bold>, all enemies with Mark lose X HP"
        }

        self.ALL_EFFECTS = {**self.PLAYER_BUFFS, **self.PLAYER_DEBUFFS, **self.ENEMY_BUFFS, **self.ENEMY_DEBUFFS}

    def init_effects(self, entity, get_effect_group: str):
        initialized_effects = {}
        effect_groups = {'Debuffs': {'Player': self.PLAYER_DEBUFFS, 'Enemy': self.ENEMY_DEBUFFS}, 'Buffs': {'Player': self.PLAYER_BUFFS, 'Enemy': self.ENEMY_BUFFS}}
        for buff in effect_groups[get_effect_group][entity.__class__.__name__]:
            if buff not in self.NON_STACKING_EFFECTS:
                initialized_effects[buff] = 0
            else:
                initialized_effects[buff] = False
        return initialized_effects

    def apply_effect(self, target, effect_name: str,  amount=0, user=None):
        current_relics = [relic.get('Name') for relic in user.relics] if getattr(user, 'player_class') in str(user) else []
        color = 'debuff' if amount < 0 or (effect_name in self.ENEMY_DEBUFFS or effect_name in self.PLAYER_DEBUFFS) else 'buff'
        if str(user) == 'Player' and effect_name in ('Weak', 'Frail'):
            if 'Turnip' in current_relics and effect_name == 'Frail':
                ansiprint('<debuff>Frail</debuff> was blocked by your <bold>Turnip</bold>.')
            elif 'Ginger' in current_relics and effect_name == 'Weak':
                ansiprint('<debuff>Weak</debuff> was blocked by <bold>Ginger</bold>')
            return
        if effect_name not in self.ALL_EFFECTS:
            raise NameError(f"'{effect_name}' is not a valid debuff or buff.")
        if ((effect_name in self.ENEMY_DEBUFFS or effect_name in self.PLAYER_DEBUFFS) or amount < 0) and target.buffs['Artifact'] > 0:
            subject = getattr('third_person_ref', 'Your')
            ansiprint(f"<debuff>{effect_name}</debuff> was blocked by {subject} <buff>Artifact</buff>.")
        else:
            if effect_name in self.NON_STACKING_EFFECTS:
                target.debuffs[effect_name] = True
            else:
                target.debuffs[effect_name] += amount
            if user:
                ansiprint(f"{'You' if str(target) != 'Enemy' else target.name} applied{(' ' + str(amount)) if effect_name not in self.NON_STACKING_EFFECTS else ''} <{color}>{effect_name}</{color}> to {target.name if 'Enemy' in str(target) else 'You'}")
            else:
                ansiprint(f"{'You' if 'Player' in str(target) else target.name} gained{(' ' + str(amount)) if effect_name not in self.NON_STACKING_EFFECTS else ''} <{color}>{effect_name}</{color}>.")
            if 'Champion Belt' in current_relics and 'Player' in str(user):
                self.apply_effect(target, 'Weak', 1, user)

    def tick_effects(self, subject):
        for buff in subject.buffs:
            if buff in self.REMOVE_ON_TURN and subject.buffs.get(buff, 0) > 0:
                subject.buffs[buff] = 0
                ansiprint(f'<buff>{buff}</buff> wears off.')
            elif buff in self.DURATION_EFFECTS and subject.buffs.get(buff, 0) > 0:
                subject.buffs[buff] -= 1
                if subject.buffs[buff] == 0:
                    ansiprint(f"<buff>{buff}</buff> wears off.")
        for debuff in subject.debuffs:
            if debuff in self.REMOVE_ON_TURN and subject.debuffs.get(debuff, 0) > 0:
                subject.debuffs[debuff] = 0
                ansiprint(f'<debuff>{debuff}</debuff> wears off.')
                continue
            if debuff in self.DURATION_EFFECTS and subject.debuffs.get(debuff, 0) > 0:
                subject.debuffs[debuff] -= 1
                if subject.debuffs[debuff] == 0:
                    ansiprint(f"<debuff>{debuff}</debuff> wears off.")

    def full_view(self, entity, enemies):
        ansiprint(f"<bold>{entity.name}</bold>")
        for buff in entity.buffs:
            if int(entity.buffs[buff]) > 0:
                ansiprint(f"<buff>{buff}</buff>: {self.ALL_EFFECTS[buff].replace('X', entity.buffs[buff])}")
        for debuff in entity.debuffs:
            if int(entity.debuffs[debuff]) > 0:
                ansiprint(f"<debuff>{debuff}</debuff>: {self.ALL_EFFECTS[debuff].replace('X', entity.debuff[debuff])}")
        for enemy in enemies:
            ansiprint(f"<bold>{enemy.name}</bold>:")
            for buff in enemy.buffs:
                if int(enemy.buffs[buff]) > 0:
                    ansiprint(f"<buff>{buff}</buff>: {self.ALL_EFFECTS[buff].replace('X', enemy.buffs[buff])}")
            for debuff in enemy.debuffs:
                if int(enemy.debuffs[debuff]) > 0:
                    ansiprint(f"<debuff>{debuff}</debuff>: {self.ALL_EFFECTS[debuff].replace('X', enemy.debuffs[debuff])}")
ei = EffectInterface()
