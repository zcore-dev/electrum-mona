import shutil
import tempfile
import sys
import os
import json
from decimal import Decimal
import time

from io import StringIO
from electrum_mona.storage import WalletStorage
from electrum_mona.json_db import FINAL_SEED_VERSION
from electrum_mona.wallet import (Abstract_Wallet, Standard_Wallet, create_new_wallet,
                             restore_wallet_from_text, Imported_Wallet)
from electrum_mona.exchange_rate import ExchangeBase, FxThread
from electrum_mona.util import TxMinedInfo
from electrum_mona.bitcoin import COIN
from electrum_mona.json_db import JsonDB
from electrum_mona.simple_config import SimpleConfig

from . import ElectrumTestCase


class FakeSynchronizer(object):

    def __init__(self):
        self.store = []

    def add(self, address):
        self.store.append(address)


class WalletTestCase(ElectrumTestCase):

    def setUp(self):
        super(WalletTestCase, self).setUp()
        self.user_dir = tempfile.mkdtemp()
        self.config = SimpleConfig({'electrum_path': self.user_dir})

        self.wallet_path = os.path.join(self.user_dir, "somewallet")

        self._saved_stdout = sys.stdout
        self._stdout_buffer = StringIO()
        sys.stdout = self._stdout_buffer

    def tearDown(self):
        super(WalletTestCase, self).tearDown()
        shutil.rmtree(self.user_dir)
        # Restore the "real" stdout
        sys.stdout = self._saved_stdout


class TestWalletStorage(WalletTestCase):

    def test_read_dictionary_from_file(self):

        some_dict = {"a":"b", "c":"d"}
        contents = json.dumps(some_dict)
        with open(self.wallet_path, "w") as f:
            contents = f.write(contents)

        storage = WalletStorage(self.wallet_path, manual_upgrades=True)
        self.assertEqual("b", storage.get("a"))
        self.assertEqual("d", storage.get("c"))

    def test_write_dictionary_to_file(self):

        storage = WalletStorage(self.wallet_path)

        some_dict = {
            u"a": u"b",
            u"c": u"d",
            u"seed_version": FINAL_SEED_VERSION}

        for key, value in some_dict.items():
            storage.put(key, value)
        storage.write()

        with open(self.wallet_path, "r") as f:
            contents = f.read()
        d = json.loads(contents)
        for key, value in some_dict.items():
            self.assertEqual(d[key], value)

class FakeExchange(ExchangeBase):
    def __init__(self, rate):
        super().__init__(lambda self: None, lambda self: None)
        self.quotes = {'TEST': rate}

class FakeFxThread:
    def __init__(self, exchange):
        self.exchange = exchange
        self.ccy = 'TEST'

    remove_thousands_separator = staticmethod(FxThread.remove_thousands_separator)
    timestamp_rate = FxThread.timestamp_rate
    ccy_amount_str = FxThread.ccy_amount_str
    history_rate = FxThread.history_rate

class FakeWallet:
    def __init__(self, fiat_value):
        super().__init__()
        self.fiat_value = fiat_value
        self.db = JsonDB("{}", manual_upgrades=True)
        self.db.transactions = self.db.verified_tx = {'abc':'Tx'}

    def get_tx_height(self, txid):
        # because we use a current timestamp, and history is empty,
        # FxThread.history_rate will use spot prices
        return TxMinedInfo(height=10, conf=10, timestamp=int(time.time()), header_hash='def')

    default_fiat_value = Abstract_Wallet.default_fiat_value
    price_at_timestamp = Abstract_Wallet.price_at_timestamp
    class storage:
        put = lambda self, x: None

txid = 'abc'
ccy = 'TEST'

class TestFiat(ElectrumTestCase):
    def setUp(self):
        super().setUp()
        self.value_sat = COIN
        self.fiat_value = {}
        self.wallet = FakeWallet(fiat_value=self.fiat_value)
        self.fx = FakeFxThread(FakeExchange(Decimal('1000.00100000')))
        default_fiat = Abstract_Wallet.default_fiat_value(self.wallet, txid, self.fx, self.value_sat)
        self.assertEqual(Decimal('1000.00100000'), default_fiat)
        self.assertEqual('1,000.00100000', self.fx.ccy_amount_str(default_fiat, commas=True))

    def test_save_fiat_and_reset(self):
        self.assertEqual(False, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1000.01000000', self.fx, self.value_sat))
        saved = self.fiat_value[ccy][txid]
        self.assertEqual('1,000.01000000', self.fx.ccy_amount_str(Decimal(saved), commas=True))
        self.assertEqual(True,       Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '', self.fx, self.value_sat))
        self.assertNotIn(txid, self.fiat_value[ccy])
        # even though we are not setting it to the exact fiat value according to the exchange rate, precision is truncated away
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1,000.001000001', self.fx, self.value_sat))

    def test_too_high_precision_value_resets_with_no_saved_value(self):
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1,000.00100000', self.fx, self.value_sat))

    def test_empty_resets(self):
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '', self.fx, self.value_sat))
        self.assertNotIn(ccy, self.fiat_value)

    def test_save_garbage(self):
        self.assertEqual(False, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, 'garbage', self.fx, self.value_sat))
        self.assertNotIn(ccy, self.fiat_value)


class TestCreateRestoreWallet(WalletTestCase):

    def test_create_new_wallet(self):
        passphrase = 'mypassphrase'
        password = 'mypassword'
        encrypt_file = True
        d = create_new_wallet(path=self.wallet_path,
                              passphrase=passphrase,
                              password=password,
                              encrypt_file=encrypt_file,
                              gap_limit=1,
                              config=self.config)
        wallet = d['wallet']  # type: Standard_Wallet
        wallet.check_password(password)
        self.assertEqual(passphrase, wallet.keystore.get_passphrase(password))
        self.assertEqual(d['seed'], wallet.keystore.get_seed(password))
        self.assertEqual(encrypt_file, wallet.storage.is_encrypted())

    def test_restore_wallet_from_text_mnemonic(self):
        text = 'bitter grass shiver impose acquire brush forget axis eager alone wine silver'
        passphrase = 'mypassphrase'
        password = 'mypassword'
        encrypt_file = True
        d = restore_wallet_from_text(text,
                                     path=self.wallet_path,
                                     passphrase=passphrase,
                                     password=password,
                                     encrypt_file=encrypt_file,
                                     gap_limit=1,
                                     config=self.config)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(passphrase, wallet.keystore.get_passphrase(password))
        self.assertEqual(text, wallet.keystore.get_seed(password))
        self.assertEqual(encrypt_file, wallet.storage.is_encrypted())
        self.assertEqual('mona1q2ccr34wzep58d4239tl3x3734ttle92arr4e30', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_xpub(self):
        text = 'zpub6nsHdRuY92FsMKdbn9BfjBCG6X8pyhCibNP6uDvpnw2cyrVhecvHRMa3Ne8kdJZxjxgwnpbHLkcR4bfnhHy6auHPJyDTQ3kianeuVLdkCYQ'
        d = restore_wallet_from_text(text, path=self.wallet_path, gap_limit=1, config=self.config)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(text, wallet.keystore.get_master_public_key())
        self.assertEqual('mona1q3g5tmkmlvxryhh843v4dz026avatc0zz8fpnsg', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_xkey_that_is_also_a_valid_electrum_seed_by_chance(self):
        text = 'yprvAJBpuoF4FKpK92ofzQ7ge6VJMtorow3maAGPvPGj38ggr2xd1xCrC9ojUVEf9jhW5L9SPu6fU2U3o64cLrRQ83zaQGNa6YP3ajZS6hHNPXj'
        d = restore_wallet_from_text(text, path=self.wallet_path, gap_limit=1, config=self.config)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(text, wallet.keystore.get_master_private_key(password=None))
        self.assertEqual('PWUDw6HSqGgeThm13gCWVNzu8rBhwGFx96', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_xprv(self):
        text = 'zprvAZswDvNeJeha8qZ8g7efN3FXYVJLaEUsE9TW6qXDEbVe74AZ75c2sZFZXPNFzxnhChDQ89oC8C5AjWwHmH1HeRKE1c4kKBQAmjUDdKDUZw2'
        d = restore_wallet_from_text(text, path=self.wallet_path, gap_limit=1, config=self.config)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(text, wallet.keystore.get_master_private_key(password=None))
        self.assertEqual('mona1q3g5tmkmlvxryhh843v4dz026avatc0zz8fpnsg', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_addresses(self):
        text = 'mona1q3g5tmkmlvxryhh843v4dz026avatc0zz8fpnsg mona1q9pzjpjq4nqx5ycnywekcmycqz0wjp2nq7urx8j'
        d = restore_wallet_from_text(text, path=self.wallet_path, config=self.config)
        wallet = d['wallet']  # type: Imported_Wallet
        self.assertEqual('mona1q3g5tmkmlvxryhh843v4dz026avatc0zz8fpnsg', wallet.get_receiving_addresses()[0])
        self.assertEqual(2, len(wallet.get_receiving_addresses()))
        # also test addr deletion
        wallet.delete_address('mona1q9pzjpjq4nqx5ycnywekcmycqz0wjp2nq7urx8j')
        self.assertEqual(1, len(wallet.get_receiving_addresses()))

    def test_restore_wallet_from_text_privkeys(self):
        text = 'p2wpkh:T6v5Q8KEmjLmJoTxPfXfyNcCEFYC7Lfmwmp9Y8dce9knevo9ZkPk p2wpkh:TAgoypi14k5Y54svysG62xp5QFRWiF1W64zxaFRFPo2jMPSMoa5D'
        d = restore_wallet_from_text(text, path=self.wallet_path, config=self.config)
        wallet = d['wallet']  # type: Imported_Wallet
        addr0 = wallet.get_receiving_addresses()[0]
        self.assertEqual('mona1q3g5tmkmlvxryhh843v4dz026avatc0zz8fpnsg', addr0)
        self.assertEqual('p2wpkh:T6v5Q8KEmjLmJoTxPfXfyNcCEFYC7Lfmwmp9Y8dce9knevo9ZkPk',
                         wallet.export_private_key(addr0, password=None)[0])
        self.assertEqual(2, len(wallet.get_receiving_addresses()))
        # also test addr deletion
        wallet.delete_address('mona1q9pzjpjq4nqx5ycnywekcmycqz0wjp2nq7urx8j')
        self.assertEqual(1, len(wallet.get_receiving_addresses()))
