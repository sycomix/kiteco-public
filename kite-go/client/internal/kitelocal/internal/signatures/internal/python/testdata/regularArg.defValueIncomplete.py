def myFunc(first="default first", second="default second", **kwargs):
    print(f"{first} |  {second}")

myFunc(kw1="kw1 value", kw2="kw2 value")
myFunc(second=<caret>)
