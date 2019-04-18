import click
from .deploy_docker import deploy as deploy_docker
from .deploy_bigdata import deploy as deploy_bigdata
from .deploy_rpm import deploy as deploy_rpm


@click.group()
def main():  # group entry
    pass


main.add_command(deploy_docker)  # add deploy_docker as subcommand
main.add_command(deploy_bigdata)  # add deploy_bigdata as subcommand
main.add_command(deploy_rpm)  # add deploy_rpm as subcommand


if __name__ == '__main__':
    main()
