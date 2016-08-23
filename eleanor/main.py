"""Main entry point for the eleanor service"""
import app


def main():
    """Method to run the eleanor service"""
    app.web_app.run(port=6060)


if __name__ == '__main__':
    main()
