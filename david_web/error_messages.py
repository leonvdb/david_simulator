from david_web import planisphere


def return_error_message(reason):

    error_messages = {
        'too many verbs': """
    Du hast zu viele Verben angegeben: {verbs}.
    Bitte schreib nur ein Verb statt {verb_count}!
    """,
        'no verbs': """
    Du hast kein bekanntes Verb in deinen Befehl geschrieben!
    Bitte gib ein Verb an!
    """,
        'too many directions': """
    Du hast zu viele Richtungen angegeben: {directions}.
    Bitte schreib nur eine Richtung statt {direction_count}
    """,
        'no direction': """
    Du hast keine bekannte Richtung in deinen Befehl geschrieben!
    Bitte gib eine Richtung an wenn du dich bewegen möchtest!
    """,
        'direction unavailable': """
    Du hast kannst das angegebene Ziel von hier nicht erreichen.
    """,
        'no take objects': """
    Du hast keinen bekannten Gegenstand angegeben.
    Bitte gib ein Objekt an das du aufnehmen möchtest.
    """,
        'too many take objects': """
    Du hast zu viele Objekte angegeben: {objects}.
    Du kannst nur ein Objekt gleichzeitig aufnehmen und nicht {object_count}.
    """,
        'object not in room': """
    Das angegebene objekt \"{objects[0]}\" befindet sich nicht in diesem Bereich.
    Leider kannst du es also nicht aufnehmen...
    """,
        'object not takeable': """
    Das angegebene objekt \"{objects[0]}\" kannst du leider nicht aufnehmen.
    """,
        'too many opponents': """
    Du hast zu viele Objekte angegeben die du angreifen möchtest: {objects}.
    Du kannst nur ein Objekt gleichzeitig angreifen und nicht {object_count}.
    """,
        'no opponents': """
    Du hast kein bekanntes Objekt angegeben, dass du angreifen möchtest.
    Bitte gib einen möglichen Gegner an.
    """,
        'opponent not in room': """
    Das Objekt, dass du angreifen möchtest befindet sich nicht in diesem Raum.
    """,
        'object not attackable': """
    Das Objekt \"{objects[0]}\" kannst du nicht angrefen.
    """,
        'opponent already dead': """
    Der Gegner \"{objects[0]}\" ist bereits besiegt. Du kannst ihn nicht nochmal angrefen.
    """
    }

    message = error_messages.get(reason)
    return message
