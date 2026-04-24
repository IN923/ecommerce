from hashids import Hashids

hashids=Hashids(salt="my ecommerce project")

def encode(any_pk):
    return hashids.encode(any_pk)

def decode(any_pk):
    return hashids.decode(any_pk)

