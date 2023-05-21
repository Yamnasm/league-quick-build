import argparse

def create_parser():
    ap = argparse.ArgumentParser()
    arg_group = ap.add_mutually_exclusive_group()

    arg_group.add_argument("-s",
                           "--summonersrift",
                           action = "store_const",
                           const = True,
                           default = False)

    arg_group.add_argument("-a",
                           "--aram",
                           action = "store_const",
                           const = True,
                           default = False)

    ap.add_argument("-r",
                    "--role",
                    action = "store",
                    type = str,
                    required = False,
                    default = False)

    ap.add_argument("-c",
                    "--champ",
                    action = "store",
                    type = str,
                    required = False,
                    default = False)
    
    args = ap.parse_intermixed_args()
    return args