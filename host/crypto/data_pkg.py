import json
import pickle

from nucypher.data_sources import DataSource
from umbral.keys import UmbralPublicKey
from nucypher.crypto.kits import UmbralMessageKit
from .channel import Channel


class EncryptedDataPackage:
    '''
    Encrypted data package which contains encrypted info and neccessary information for decrypting
    '''

    def __init__(self,
                 alice_pubkey_bytes: bytes,
                 data_source_pubkey_bytes: bytes,
                 kit_bytes: bytes,
                 label_bytes: bytes,
                 policy_pubkey_bytes: bytes):

        self.alice_pubkey_bytes = alice_pubkey_bytes
        self.data_source_pubkey_bytes = data_source_pubkey_bytes
        self.kit_bytes = kit_bytes
        self.label_bytes = label_bytes
        self.policy_pubkey_bytes = policy_pubkey_bytes

    @classmethod
    def from_channel(cls, channel: Channel, data: bytes) -> object:
        '''
        Create EncryptedDataPackage from Channel & data. In other words it encrypts data usign Channel settings
        :param channel: Channel instance
        :param data: data to be encrypted
        :return: EncryptedDataPackage instance
        '''

        label_bytes = channel.label_bytes
        policy_pub_key_object = UmbralPublicKey.from_bytes(channel.policy_pubkey_bytes)
        data_source = DataSource(policy_pubkey_enc=policy_pub_key_object)
        data_source_pubkey_bytes = bytes(data_source.stamp)
        message_kit, _signature = data_source.encrypt_message(data)
        kit_bytes = message_kit.to_bytes()

        return EncryptedDataPackage(alice_pubkey_bytes=channel.alice_pubkey_bytes,
                                    data_source_pubkey_bytes=data_source_pubkey_bytes,
                                    kit_bytes=kit_bytes,
                                    label_bytes=label_bytes,
                                    policy_pubkey_bytes=channel.policy_pubkey_bytes)

    @classmethod
    def from_bytes(cls, seralized_object: bytes) -> object:
        '''
        Creates an EncryptedDataPackage from serialization
        :param seralized_object:
        :return: EncryptedDataPackage instance
        '''
        json_data = pickle.loads(seralized_object)
        return cls.from_json(json_data)

    @classmethod
    def from_json(cls, json_data: str):
        '''
        Creates an EncryptedDataPackage from JSON
        :param json:
        :return:
        '''
        try:
            dict = json.loads(json_data)

            alice_pubkey_bytes = bytes.fromhex(dict['alice_pubkey'])
            data_source_pubkey_bytes = bytes.fromhex(dict['data_source_pubkey'])
            kit_bytes = bytes.fromhex(dict['kit'])
            label_bytes = bytes.fromhex(dict['label'])
            policy_pubkey_bytes = bytes.fromhex(dict['policy_pubkey'])

        except KeyError:
            print("JSON was incorrect" + json_data)
            return None

        return EncryptedDataPackage(alice_pubkey_bytes=alice_pubkey_bytes,
                                    data_source_pubkey_bytes=data_source_pubkey_bytes,
                                    kit_bytes=kit_bytes,
                                    label_bytes=label_bytes,
                                    policy_pubkey_bytes=policy_pubkey_bytes)

    def decrypt(self, channel_reader: object) -> bytes:
        '''
        Decrypt extsting message using ChannelReader instance
        :param BOB:
        :return:
        '''
        policy_pubkey_restored = UmbralPublicKey.from_bytes(self.policy_pubkey_bytes)

        data_source_restored = DataSource.from_public_keys(
            policy_public_key=policy_pubkey_restored,
            datasource_public_key=self.data_source_pubkey_bytes,
            label=self.label_bytes)

        channel_reader.BOB.join_policy(self.label_bytes, self.alice_pubkey_bytes)

        alices_sig_pubkey = UmbralPublicKey.from_bytes(bytes(self.alice_pubkey_bytes))
        message_kit_object = UmbralMessageKit.from_bytes(self.kit_bytes)

        return channel_reader.BOB.retrieve(
            message_kit=message_kit_object,
            data_source=data_source_restored,
            alice_verifying_key=alices_sig_pubkey)

    def to_bytes(self) -> bytes:
        '''
        Serialize object into bytes
        :return:
        '''
        return pickle.dumps(self.to_json())

    def to_json(self) -> str:
        '''
        Serialize object into JSON
        :return:
        '''
        dict = {
            'alice_pubkey': self.alice_pubkey_bytes.hex(),
            'data_source_pubkey': self.data_source_pubkey_bytes.hex(),
            'kit': self.kit_bytes.hex(),
            'label': self.label_bytes.hex(),
            'policy_pubkey': self.policy_pubkey_bytes.hex(),
            }

        return json.dumps(dict)







