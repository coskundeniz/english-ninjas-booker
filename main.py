from argparse import ArgumentParser
from booker import Booker
from reporter import Reporter


def get_arg_parser():
    """Get argument parser

    :rtype: ArgumentParser
    :returns: ArgumentParser object
    """

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-e", "--email", help="Email for login")
    arg_parser.add_argument("-p", "--password", help="Password for login")
    arg_parser.add_argument("-o", "--output", help="Write report to given file")

    return arg_parser


def main():

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    booker = Booker()

    if args.email and args.password:
        booker.login_to_page(args.email, args.password)
    else:
        booker.login_to_page()
    
    if args.output:
        Reporter.set_output_file(args.output)

    booker.book_session()


if __name__ == '__main__':

    main()

