import argparse
from .commands import generator, runner, register, process

def main(argv=None):
    
    parser = argparse.ArgumentParser(description="Linnea Inspector CLI",
                                     usage="linnea-inspector <command>",
                                     epilog="Use 'linnea-inspector <command> --help' for more information on a specific command.")
    subparsers = parser.add_subparsers(dest="command", required=True,  title="commands",)
    generator.add_parser(subparsers)
    runner.add_parser(subparsers)
    register.add_parser(subparsers)
    process.add_parser(subparsers)

    # run.add_parser(subparsers)
    # process.add_parser(subparsers)
    subparsers.add_parser("inspector", help="Launch the Linnea Inspector web application.")
    subparsers.add_parser("store", help="Lauch the Linnea Inspector store web application.")

    args, params = parser.parse_known_args(argv)

    if args.command == "inspector":
        from .widget.inspector import main as inspector_main
        inspector_main()
    elif args.command == "store":
        from .widget.store import main as store_main
        store_main()
    elif args.command == "generator":
        generator.generator(args, params)
    elif args.command == "runner":
        runner.runner(args)
    elif args.command == "register":
        register.register(args)
    elif args.command == "process":
        process.process(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")
    
    
if __name__ == "__main__":
    main()