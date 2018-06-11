class ParserError(Exception):
    pass

class Sentence(object):

    def __init__(self, subject, verb, obj):
        self.subject = subject[1]
        self.verb = verb[1]
        self.object = obj[1]

class Clean(object):

    def __init__(self, word_list):
        self.word_list = word_list

    def clean_it(self):
        limit = len(self.word_list)
        tuple_position = 0
        counter = 0

        while counter < limit:
            word_pair = self.word_list[tuple_position]

            if word_pair[0] == 'error' or word_pair[0] == 'stop':
                self.word_list.pop(tuple_position)
            else:
                tuple_position += 1
            counter += 1
        return self.word_list

class Parser(object):

    def __init__(self, clean_words):
        self.clean_words = clean_words

    def assemble(self):

        subj = None
        verb = None
        obj = None
        scan_for = 'subject'

        if self.clean_words:

            for word in self.clean_words:

                if scan_for == 'subject' and word[0] == 'noun':
                    subj = word
                    scan_for = 'verb'
                    continue
                elif scan_for == 'subject' and word[0] == 'verb':
                    subj = ('noun', 'player')
                    scan_for = 'verb'
                    continue
                elif scan_for == 'subject' and word[0] == None:
                    raise ParserError("Expected a noun or a verb next.")
                else:
                    pass

                if scan_for == 'verb' and word[0] == 'verb':
                    verb = word
                    scan_for = 'object'
                    continue
                elif scan_for == 'verb' and word[0] == 'noun':
                    raise ParserError("Expected a verb next.")
                else:
                    pass

                if scan_for == 'object' and word[0] == 'noun':
                    obj = word
                    continue
                else:
                    pass
        else:
            raise ParserError("The string is empty.")

        return Sentence(subj, verb, obj)
