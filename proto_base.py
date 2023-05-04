import google.protobuf.message

class ProtobufMessage(google.protobuf.message.Message):

    def __init__(self):
        super().__init__()

        # Initialize all fields to their default values.
        for field in self.DESCRIPTOR.fields:
            setattr(self, field.name, field.default_value)

    def __eq__(self, other):
        """Returns True if the two messages are equal."""
        if not isinstance(other, ProtobufMessage):
            return False

        for field in self.DESCRIPTOR.fields:
            if getattr(self, field.name) != getattr(other, field.name):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """Returns a hash value for the message."""
        h = 0
        for field in self.DESCRIPTOR.fields:
            h = h * 31 + hash(getattr(self, field.name))
        return h

    def __repr__(self):
        """Returns a string representation of the message."""
        return "{}({})".format(self.__class__.__name__, self.__dict__)

    def to_bytes(self):
        """Serializes the message to a binary string."""
        return self.SerializeToString()

    def from_bytes(self, data):
        """Deserializes the message from a binary string."""
        self.ParseFromString(data)
