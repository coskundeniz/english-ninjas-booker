
class Reporter:
    """Report booking results to either file or stdout

    Attributes:
        output_file (str)  Name of output file
    """

    output_file = None

    @classmethod
    def set_output_file(cls, filename):
        """Set the name of output file
    
        :type filename: str
        :param filename: Name of output file
        """
        cls.output_file = filename

    def print_results(self, results):
        """Print booking results.

        If output file is given, write results to file,
        otherwise print to stdout.

        :type results: list
        :param results: List of BookingResult objects
        """

        if not Reporter.output_file:
            print(f"\n{'#'*70}\n")

            for result in results:
                print(result.message)

            print(f"\n{'#'*70}\n")
        else:
            with open(Reporter.output_file, "w") as output:
                output.writelines([result.message+"\n\n" for result in results])


