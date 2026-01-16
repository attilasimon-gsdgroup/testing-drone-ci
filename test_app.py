from app import greet

def test_default():
    assert greet() == "Hello, Drone-CI!"

if __name__ == "__main__":
    try:
        test_default()
        print("PASS")
    except AssertionError:
        print("FAIL")
        raise SystemExit(1)
