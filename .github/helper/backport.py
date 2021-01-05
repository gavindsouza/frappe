import sys

if __name__ == "__main__":
    args = sys.argv
    pr = args[1]
    comment_body = " ".join(args[2:])

    print(pr)
    print(comment_body)