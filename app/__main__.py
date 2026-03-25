from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    from app.entrypoint import main

    main()