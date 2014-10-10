import logging
from app import create_app, run



if __name__ == "__main__":
    logging.basicConfig(filename="log/daily.log", level=logging.INFO,
                        format="%(levelname)s @ %(asctime)s: %(message)s")
    logging.info("Starting Server")
    app = create_app()
    run()
