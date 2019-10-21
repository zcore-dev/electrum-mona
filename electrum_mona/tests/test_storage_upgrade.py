import shutil
import tempfile
import os

from electrum_mona.storage import WalletStorage
from electrum_mona.wallet import Wallet
from electrum_mona import constants

from .test_wallet import WalletTestCase


# TODO add other wallet types: 2fa, xpub-only
# TODO hw wallet with client version 2.6.x (single-, and multiacc)
class TestStorageUpgrade(WalletTestCase):

    def testnet_wallet(func):
        # note: it's ok to modify global network constants in subclasses of SequentialTestCase
        def wrapper(self, *args, **kwargs):
            constants.set_testnet()
            try:
                return func(self, *args, **kwargs)
            finally:
                constants.set_mainnet()
        return wrapper

##########

    def test_upgrade_from_client_2_9_3_seeded(self):
        wallet_str = '{"addr_history": {"M86vvgYRgPBW3QfyUnxbKBeUzbGtgp6NXG": [],"M98MvBtibhTcnz8tLPNk3ooFDE5qpck83r": [],"M9caHU9o66Wvmc2gqqW2DHPcnshqdj36kG": [],"MABcFFZv7v3FRAEKU5kqoB6xt9VKupEt8K": [],"MAeRNwBYorbvbeAwiJfp7cEiPHThPhcut2": [],"MBMpHGd7nKhFn7SPYkNb2SJd8WiGpTH5aB": [],"MBavRPSte8woScUxXQwybiwvvWNpEZ1WWy": [],"MC9S8ipqNu4pjodYA7ns6sS15GEEUqeuU3": [],"MEhUENYZXhwuKtiCYep6AjpRGqLBLLxa4y": [],"MFbXqsdyVSnEGmGMpduND5kp93ExhYgtbu": [],"MFgJcgrbEnV1ANbPcAsAV7ADBF63NEpXK3": [],"MGUJMzZeA1PBUsv3rUNcjLzVnAjaWkS95n": [],"MGtCxT8kLcqqi66Spwr98JnYSYJHU7ShGZ": [],"MGwggCpjuwpCfbjTCbYoX1ngzNSUnTEtEn": [],"MLoyw8Bt5zVoVRcFxUPbKuW5FF3NNfLUVf": [],"MLy8usGiKXVqo4VtWAUq1jdgKASdN8JTij": [],"MPMNgAeu7B6PTr9WVM9mhRycmQVy14VUvL": [],"MPQzvFN6fvcdwZC1KsrjagZizdFx46yp1V": [],"MPbw4Njqk6neGMcBNmxHpDjxoBGbMPwJiL": [],"MQycguJjCxpW7qBGKHPptGqMVUP28VJhp6": [],"MRR8gRePoj33M9Sx4UDEAC1fdLhppit71k": [],"MSJTC3sSuVSyQ2Fehrxg5UkwpYQn2bkNjC": [],"MSeTEqGyJfAD6TxsFgfGwMtvWf3fbaRZeW": [],"MSi7o6WRptrcpQEZBvVX2rrZdKz5WHcXyJ": [],"MSjeTpS3Kcij8GvCnatG17mPdFd3FfF3Ra": [],"MTVWS92xnBVqopgTo3F7eYqQq24b3EQpNB": [],"MUuGCeLx98GQxq1Y2UTSQbZd7PMmc2iDAs": [],"MWfHXccPyKPeY5Nf5kSk4GsCKHhsBSymxU": []},"addresses": {"change": ["MPbw4Njqk6neGMcBNmxHpDjxoBGbMPwJiL","MPMNgAeu7B6PTr9WVM9mhRycmQVy14VUvL","MC9S8ipqNu4pjodYA7ns6sS15GEEUqeuU3","MGwggCpjuwpCfbjTCbYoX1ngzNSUnTEtEn","MGtCxT8kLcqqi66Spwr98JnYSYJHU7ShGZ","MRR8gRePoj33M9Sx4UDEAC1fdLhppit71k"],"receiving": ["MBavRPSte8woScUxXQwybiwvvWNpEZ1WWy","MABcFFZv7v3FRAEKU5kqoB6xt9VKupEt8K","MGUJMzZeA1PBUsv3rUNcjLzVnAjaWkS95n","MQycguJjCxpW7qBGKHPptGqMVUP28VJhp6","MWfHXccPyKPeY5Nf5kSk4GsCKHhsBSymxU","MAeRNwBYorbvbeAwiJfp7cEiPHThPhcut2","MSJTC3sSuVSyQ2Fehrxg5UkwpYQn2bkNjC","M98MvBtibhTcnz8tLPNk3ooFDE5qpck83r","M9caHU9o66Wvmc2gqqW2DHPcnshqdj36kG","MBMpHGd7nKhFn7SPYkNb2SJd8WiGpTH5aB","MSjeTpS3Kcij8GvCnatG17mPdFd3FfF3Ra","MEhUENYZXhwuKtiCYep6AjpRGqLBLLxa4y","MLy8usGiKXVqo4VtWAUq1jdgKASdN8JTij","MFbXqsdyVSnEGmGMpduND5kp93ExhYgtbu","MSi7o6WRptrcpQEZBvVX2rrZdKz5WHcXyJ","MFgJcgrbEnV1ANbPcAsAV7ADBF63NEpXK3","M86vvgYRgPBW3QfyUnxbKBeUzbGtgp6NXG","MLoyw8Bt5zVoVRcFxUPbKuW5FF3NNfLUVf","MPQzvFN6fvcdwZC1KsrjagZizdFx46yp1V","MUuGCeLx98GQxq1Y2UTSQbZd7PMmc2iDAs","MTVWS92xnBVqopgTo3F7eYqQq24b3EQpNB","MSeTEqGyJfAD6TxsFgfGwMtvWf3fbaRZeW"]},"keystore": {"seed": "cereal wise two govern top pet frog nut rule sketch bundle logic","type": "bip32","xprv": "xprv9s21ZrQH143K29XjRjUs6MnDB9wXjXbJP2kG1fnRk8zjdDYWqVkQYUqaDtgZp5zPSrH5PZQJs8sU25HrUgT1WdgsPU8GbifKurtMYg37d4v","xpub": "xpub661MyMwAqRbcEdcCXm1sTViwjBn28zK9kFfrp4C3JUXiW1sfP34f6HA45B9yr7EH5XGzWuTfMTdqpt9XPrVQVUdgiYb5NW9m8ij1FSZgGBF"},"pruned_txo": {},"seed_type": "standard","seed_version": 14,"stored_height": 1298303,"transactions": {},"tx_fees": {},"txi": {},"txo": {},"use_encryption": false,"verified_tx3": {},"wallet_type": "standard","winpos-qt": [100,100,840,400]}'
        self._upgrade_storage(wallet_str)

    def test_upgrade_from_client_2_9_3_importedkeys(self):
        wallet_str = '{"addr_history": {"MJNDhNyzYPbcFE5uZAg2j6YyUQVdLDhuP3": []}, "addresses": {"change": [], "receiving": ["MJNDhNyzYPbcFE5uZAg2j6YyUQVdLDhuP3"]}, "keystore": {"keypairs": {"03c2725dae5de0cbf0101cf57a3aadfb301bc3b432fa8ea38515198e41df12199f": "TPxZYPTaBiwFVo5kVmBYuJctGVDMRaCLNEEu8nsxLednda1zmVGS"}, "type": "imported"}, "pruned_txo": {}, "seed_version": 13, "stored_height": 1244824, "transactions": {}, "tx_fees": {}, "txi": {}, "txo": {}, "use_encryption": false, "verified_tx3": {}, "wallet_type": "standard", "winpos-qt": [314, 230, 840, 400]}'
        self._upgrade_storage(wallet_str)

    def test_upgrade_from_client_2_9_3_watchaddresses(self):
        wallet_str = '{"addr_history": {"MFMy9FwJsV6HiN5eZDqDETw4pw52q3UGrb": []}, "addresses": ["MFMy9FwJsV6HiN5eZDqDETw4pw52q3UGrb"], "pruned_txo": {}, "seed_version": 13, "stored_height": 1244820, "transactions": {}, "tx_fees": {}, "txi": {}, "txo": {}, "verified_tx3": {}, "wallet_type": "imported", "winpos-qt": [100, 100, 840, 400]}'
        self._upgrade_storage(wallet_str)

    def test_upgrade_from_client_2_9_3_multisig(self):
        wallet_str = '{"addr_history": {"P8ot4kcLZQaFfEV7RjVktxi7GQ1LUgDV1F": [],"P9HLyBSBSSy3JZ6cQYG6UkCiQoB6ZsPZ6Z": [],"PA9ZadzWaMXEEEBfmJy3ekhnpm3BU7mQyE": [],"PAFZUHzrhi8a3yfu9StTo7i1fy7xhc5GMp": [],"PAq4wHvvJsKLeFvRKtGA19Dj5gywwju5V2": [],"PCnkbJvEgHwmy6Lx6bvVYxUSziUpdmgx4i": [],"PDtrWfnff4DBcxGyBB1fnMpg7gv1XrYZsQ": [],"PEkj8tn89LfdKCr3AqC56BrXFKeoc1a3vP": [],"PF4BYeRwvnb8T6PXVfEw6zcVBEuujUqHCy": [],"PFAiWWB7TMVWyYmUPjE3489MhSSvTpFk1p": [],"PH94CH7MDa5tRkAkzGRwrMPuFhvTL5nsRL": [],"PHUSkFkwWP9hsMtjiBzkLyhP7NgEh3RjhA": [],"PL4NEabh2Q7yZEhY7TFSyq7JQEZ7zr65X2": [],"PPDDRcW6SvwcY68HBHPnFgQ1FmaRxCTWBf": [],"PPuJCCfP24gyUkLH8bVG4WJoFuw1Vktk47": [],"PQbo5pSf85CNH65W8zfXx1jVbvpkXFAH4q": [],"PRbupBpgfzRjoRGNqxERvzavJxRYPiDhfL": [],"PRnKJNuZpXDzJkWVTczMKUcQabWJVQX251": [],"PSJy76AemtebcepCwbsxnKoKVBwt94UbWD": [],"PSRoFQvkAmBqt151uNxH4ZB15NWVYC6JNQ": [],"PSTsTodTzJoHsHtUhCYoK5Lpu6TXHQ5Udm": [],"PSYcYiD1FaXpJAjFYkwN5opsrLMhQdphfz": [],"PSyjnkncpTntycMfaQTjdA7dDYWExKsnGD": [],"PT4Z5AjuZDCFXpFiDh8dcqujuGygadMkCd": [],"PVwTXpiNsH5gmaxHyCFinvXtByxhM3hSoF": [],"PWaXrnSr5QbnfYiwC6n1Tww8vs3BTUKRC6": [],"PWfGT1PQ5EXmrhjqJVeE4HUZcvNfhiRj9P": []},"addresses": {"change": ["P8ot4kcLZQaFfEV7RjVktxi7GQ1LUgDV1F","PRbupBpgfzRjoRGNqxERvzavJxRYPiDhfL","PPDDRcW6SvwcY68HBHPnFgQ1FmaRxCTWBf","PT4Z5AjuZDCFXpFiDh8dcqujuGygadMkCd","PAFZUHzrhi8a3yfu9StTo7i1fy7xhc5GMp","PH94CH7MDa5tRkAkzGRwrMPuFhvTL5nsRL"],"receiving": ["PVwTXpiNsH5gmaxHyCFinvXtByxhM3hSoF","PA9ZadzWaMXEEEBfmJy3ekhnpm3BU7mQyE","PL4NEabh2Q7yZEhY7TFSyq7JQEZ7zr65X2","PHUSkFkwWP9hsMtjiBzkLyhP7NgEh3RjhA","PPuJCCfP24gyUkLH8bVG4WJoFuw1Vktk47","PDtrWfnff4DBcxGyBB1fnMpg7gv1XrYZsQ","PEkj8tn89LfdKCr3AqC56BrXFKeoc1a3vP","PF4BYeRwvnb8T6PXVfEw6zcVBEuujUqHCy","PFAiWWB7TMVWyYmUPjE3489MhSSvTpFk1p","PAq4wHvvJsKLeFvRKtGA19Dj5gywwju5V2","PSyjnkncpTntycMfaQTjdA7dDYWExKsnGD","PSRoFQvkAmBqt151uNxH4ZB15NWVYC6JNQ","PSJy76AemtebcepCwbsxnKoKVBwt94UbWD","PSTsTodTzJoHsHtUhCYoK5Lpu6TXHQ5Udm","P9HLyBSBSSy3JZ6cQYG6UkCiQoB6ZsPZ6Z","PSYcYiD1FaXpJAjFYkwN5opsrLMhQdphfz","PRnKJNuZpXDzJkWVTczMKUcQabWJVQX251","PWaXrnSr5QbnfYiwC6n1Tww8vs3BTUKRC6","PWfGT1PQ5EXmrhjqJVeE4HUZcvNfhiRj9P","PCnkbJvEgHwmy6Lx6bvVYxUSziUpdmgx4i","PQbo5pSf85CNH65W8zfXx1jVbvpkXFAH4q"]},"pruned_txo": {},"seed_version": 14,"stored_height": 1479743,"transactions": {},"tx_fees": {},"txi": {},"txo": {},"use_encryption": false,"verified_tx3": {},"wallet_type": "2of2","winpos-qt": [100,100,840,400],"x1/": {"seed": "speed cruise market wasp ability alarm hold essay grass coconut tissue recipe","type": "bip32","xprv": "xprv9s21ZrQH143K48ig2wcAuZoEKaYdNRaShKFR3hLrgwsNW13QYRhXH6gAG1khxim6dw2RtAzF8RWbQxr1vvWUJFfEu2SJZhYbv6pfreMpuLB","xpub": "xpub661MyMwAqRbcGco98y9BGhjxscP7mtJJ4YB1r5kUFHQMNoNZ5y1mptze7J37JypkbrmBdnqTvSNzxL7cE1FrHg16qoj9S12MUpiYxVbTKQV"},"x2/": {"type": "bip32","xprv": null,"xpub": "xpub661MyMwAqRbcGrCDZaVs9VC7Z6579tsGvpqyDYZEHKg2MXoDkxhrWoukqvwDPXKdxVkYA6Hv9XHLETptfZfNpcJZmsUThdXXkTNGoBjQv1o"}}'
        self._upgrade_storage(wallet_str)


##########

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from electrum_mona.plugin import Plugins
        from electrum_mona.simple_config import SimpleConfig

        cls.__electrum_path = tempfile.mkdtemp()
        config = SimpleConfig({'electrum_path': cls.__electrum_path})

        gui_name = 'cmdline'
        # TODO it's probably wasteful to load all plugins... only need Trezor
        Plugins(config, gui_name)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.__electrum_path)

    def _upgrade_storage(self, wallet_json, accounts=1):
        if accounts == 1:
            # test manual upgrades
            storage = self._load_storage_from_json_string(wallet_json=wallet_json,
                                                          path=self.wallet_path,
                                                          manual_upgrades=True)
            self.assertFalse(storage.requires_split())
            if storage.requires_upgrade():
                storage.upgrade()
                self._sanity_check_upgraded_storage(storage)
            # test automatic upgrades
            path2 = os.path.join(self.user_dir, "somewallet2")
            storage2 = self._load_storage_from_json_string(wallet_json=wallet_json,
                                                           path=path2,
                                                           manual_upgrades=False)
            storage2.write()
            self._sanity_check_upgraded_storage(storage2)
            # test opening upgraded storages again
            s1 = WalletStorage(path2, manual_upgrades=False)
            self._sanity_check_upgraded_storage(s1)
            s2 = WalletStorage(path2, manual_upgrades=True)
            self._sanity_check_upgraded_storage(s2)
        else:
            storage = self._load_storage_from_json_string(wallet_json=wallet_json,
                                                          path=self.wallet_path,
                                                          manual_upgrades=True)
            self.assertTrue(storage.requires_split())
            new_paths = storage.split_accounts()
            self.assertEqual(accounts, len(new_paths))
            for new_path in new_paths:
                new_storage = WalletStorage(new_path, manual_upgrades=False)
                self._sanity_check_upgraded_storage(new_storage)

    def _sanity_check_upgraded_storage(self, storage):
        self.assertFalse(storage.requires_split())
        self.assertFalse(storage.requires_upgrade())
        w = Wallet(storage, config=self.config)

    @staticmethod
    def _load_storage_from_json_string(*, wallet_json, path, manual_upgrades):
        with open(path, "w") as f:
            f.write(wallet_json)
        storage = WalletStorage(path, manual_upgrades=manual_upgrades)
        return storage
