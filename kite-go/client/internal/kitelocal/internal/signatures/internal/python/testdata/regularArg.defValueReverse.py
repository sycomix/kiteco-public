def myFunc(first="default first", second="default second"):
    return f"{first} |  {second}"

myFunc(second="my 2nd"<caret>, first="my 1st")
