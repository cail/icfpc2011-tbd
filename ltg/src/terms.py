from rules import card_by_name


App = tuple

def check_term(term):
    if isinstance(term, App):
        left, right = term
        check_term(left)
        check_term(right)
    else:
        assert term in card_by_name.values()
        

