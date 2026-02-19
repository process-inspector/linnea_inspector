import argparse
from .commands import generator, runner, register, process, clean, sbatch, store, widget

def main(argv=None):
    
    parser = argparse.ArgumentParser(description="Linnea Inspector CLI",
                                     usage="linnea-inspector <command>",
                                     epilog="Use 'linnea-inspector <command> --help' for more information on a specific command.")
    subparsers = parser.add_subparsers(dest="command", required=True,  title="commands",)
    generator.add_parser(subparsers)
    runner.add_parser(subparsers)
    register.add_parser(subparsers)
    process.add_parser(subparsers)
    clean.add_parser(subparsers)
    sbatch.add_parser(subparsers)
    store.add_parser(subparsers)
    widget.add_parser(subparsers)

    # run.add_parser(subparsers)
    # process.add_parser(subparsers)
    # subparsers.add_parser("widget", help="Launch the Linnea Inspector web application.")
    # subparsers.add_parser("widget-store", help="Lauch the web application to modify store data.")

    args, params = parser.parse_known_args(argv)

    if args.command == "widget":
        widget.widget(args)
    elif args.command == "generator":
        generator.generator(args, params)
    elif args.command == "runner":
        runner.runner(args)
    elif args.command == "register":
        register.register(args)
    elif args.command == "process":
        process.process(args)
    elif args.command == "clean":
        clean.clean(args)
    elif args.command == "sbatch":
        sbatch.sbatch(args, params)
    elif args.command == "store":
        store.store(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")
    
    
if __name__ == "__main__":
    main()