from autoapply.linkedin.answers import PhraseMatcher


def test_phrase_similarity_works_with_string_input():
    phrase = "apple pie"
    phrase_list = ["apple", "apple cider", "banana", "apple pie with ice cream"]
    phrase_matcher = PhraseMatcher(phrase, phrase_list)
    closest_phrase = phrase_matcher.find_closest_phrases()
    assert closest_phrase == "apple"
    assert phrase_matcher.similarities == [
        [('apple', 0.5725255144931797), ('apple cider', 0.2810214227199534), ('banana', 0.0),
         ('apple pie with ice cream', 0.4939755204387003)]]


def test_phrase_similarity_works_with_list_input():
    phrases = ["apple pie", "banana smoothie"]
    phrase_list = ["apple", "apple cider", "banana", "apple pie with ice cream", "orange"]
    phrase_matcher = PhraseMatcher(phrases, phrase_list)
    closest_phrase = phrase_matcher.find_closest_phrases()
    assert closest_phrase == ["apple", "banana"]
    assert phrase_matcher.similarities == [
        [('apple', 0.5959400344623714), ('apple cider', 0.31256422187672245), ('banana', 0.0),
         ('apple pie with ice cream', 0.5124759281221004), ('orange', 0.0)],
        [('apple', 0.0), ('apple cider', 0.0), ('banana', 0.6387085483562188), ('apple pie with ice cream', 0.0),
         ('orange', 0.0)]]
