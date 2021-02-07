def get_coin_name(text):
    try:
        return text[text.index("$"):].split(" ")[0][1:]
    except ValueError:
        return None

    

if __name__ == "__main__":
    assert get_coin_name("coi is: $dfs (dfdf) ") != None
    assert get_coin_name("coi is: dfs (dfdf) ") == None
    assert get_coin_name("coi is: $dfs (dfdf) ") == "dfs"