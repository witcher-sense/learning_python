from hashlib import sha256
import base58
import binascii

class PublicKey:
    """Calculating a public key using private key"""
    def __init__(self, private_key):   
       self.private_key = private_key
       self.Pcurve = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1 # The proven prime
       self.N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 # Number of points in the field
       self.Acurve = 0; self.Bcurve = 7 # These two defines the elliptic curve. y^2 = x^3 + Acurve * x + Bcurve
       self.Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
       self.Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
       self.GPoint = (self.Gx, self.Gy) # This is our generator point. Trillions of dif ones possible

    def privateWIF(self):

        self.private_wif = f"80{hex(self.private_key)[2:]}"
        self.private_wif_comp = f"80{hex(self.private_key)[2:]}01"
        self.checksum = sha256(binascii.unhexlify(self.private_wif)).hexdigest()
        self.checksum = sha256(binascii.unhexlify(self.checksum)).hexdigest()[:8]
        self.checksum_comp = sha256(binascii.unhexlify(self.private_wif_comp)).hexdigest()
        self.checksum_comp = sha256(binascii.unhexlify(self.checksum_comp)).hexdigest()[:8]

        self.private_wif = f"{self.private_wif}{self.checksum}"
        self.private_wif_comp = f"{self.private_wif_comp}{self.checksum_comp}"

        self.private_wif = base58.b58encode(bytes.fromhex(self.private_wif)).decode("UTF-8")
        self.private_wif_comp = base58.b58encode(bytes.fromhex(self.private_wif_comp)).decode("UTF-8")
        print(f"WIF - private key\n{self.private_wif}\n")
        print(f"WIF compressed - private key\n{self.private_wif_comp}")
        
    def modinv(self, a, n): #Extended Euclidean Algorithm/'division' in elliptic curves
        n = self.Pcurve
        lm, hm = 1,0
        low, high = a%n, n
        while low > 1:
            ratio = int(high/low)
            nm, new = int(hm-lm*ratio), int(high-low*ratio)
            lm, low, hm, high = nm, new, lm, low
        return lm % n

    def ECadd(self, a,b): # Not true addition, invented for EC. Could have been called anything.
        LamAdd = ((b[1]-a[1]) * self.modinv(b[0]-a[0],self.Pcurve)) % self.Pcurve
        x = (LamAdd*LamAdd-a[0]-b[0]) % self.Pcurve
        y = (LamAdd*(a[0]-x)-a[1]) % self.Pcurve
        return (x,y)

    def ECdouble(self, a): # This is called point doubling, also invented for EC.
        Lam = ((3*a[0]*a[0]+self.Acurve) * self.modinv((2*a[1]), self.Pcurve)) % self.Pcurve
        x = int((Lam*Lam-2*a[0]) % self.Pcurve)
        y = int((Lam*(a[0]-x)-a[1]) % self.Pcurve)
        return (x,y)

    def EccMultiply(self, GenPoint, ScalarHex): #Double & add. Not true multiplication
        if ScalarHex == 0 or ScalarHex >= self.N: raise Exception("Invalid Scalar/Private Key")
        ScalarBin = str(bin(ScalarHex))[2:]
        Q=GenPoint
        for i in range (1, len(ScalarBin)): # This is invented EC multiplication.
            Q=self.ECdouble(Q) # print "DUB", Q[0]; print
            if ScalarBin[i] == "1":
                Q=self.ECadd(Q,GenPoint) # print "ADD", Q[0]; print
        return(Q)

    def PublicCalc(self):

        public_key = self.EccMultiply(self.GPoint, self.private_key)
        print("\nthe uncompressed public key (not address):") 
        print(public_key)
        print("\nthe uncompressed public key (HEX):") 
        message = f"04{(hex(public_key[0])[2:]):064}{(hex(public_key[1])[2:]):064}"
        print(message.upper())
        print(f"Length: {len(message)}")
        print("\nthe official Public Key - compressed:") 
        if public_key[1] % 2 == 1: # If the Y value for the Public Key is odd.
            message = f"03{hex(public_key[0])[2:]:064}"
            print(message.upper())
            print(f"Length: {len(message)}")
        else: # Or else, if the Y value is even.
            message = f"02{hex(public_key[0])[2:]:064}"
            print(message.upper())
            print(f"Length: {len(message)}")

prompt  = input(f"Please insert your private key in HEX format (0x): ")

try:
    prompt = int(prompt, 16)  # interpret the input as a base-16 number, a hexadecimal.
except ValueError:
    print("You did not enter a hexadecimal number!")
my_key = PublicKey(prompt)
my_key.PublicCalc()
my_key.privateWIF()

