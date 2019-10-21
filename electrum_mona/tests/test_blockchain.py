import shutil
import tempfile
import os

from electrum_mona import constants, blockchain
from electrum_mona.simple_config import SimpleConfig
from electrum_mona.blockchain import Blockchain, deserialize_header, hash_header
from electrum_mona.util import bh2u, bfh, make_dir

from . import ElectrumTestCase


class TestBlockchain(ElectrumTestCase):

    HEADERS = {
        'A': deserialize_header(bfh("0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff7f2002000000"), 0),
        'B': deserialize_header(bfh("0000002006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f186c8dfd970a4545f79916bc1d75c9d00432f57c89209bf3bb115b7612848f509c25f45bffff7f2000000000"), 1),
        'C': deserialize_header(bfh("00000020686bdfc6a3db73d5d93e8c9663a720a26ecb1ef20eb05af11b36cdbc57c19f7ebf2cbf153013a1c54abaf70e95198fcef2f3059cc6b4d0f7e876808e7d24d11cc825f45bffff7f2000000000"), 2),
        'D': deserialize_header(bfh("00000020122baa14f3ef54985ae546d1611559e3f487bd2a0f46e8dbb52fbacc9e237972e71019d7feecd9b8596eca9a67032c5f4641b23b5d731dc393e37de7f9c2f299e725f45bffff7f2000000000"), 3),
        'E': deserialize_header(bfh("00000020f8016f7ef3a17d557afe05d4ea7ab6bde1b2247b7643896c1b63d43a1598b747a3586da94c71753f27c075f57f44faf913c31177a0957bbda42e7699e3a2141aed25f45bffff7f2001000000"), 4),
        'F': deserialize_header(bfh("000000201d589c6643c1d121d73b0573e5ee58ab575b8fdf16d507e7e915c5fbfbbfd05e7aee1d692d1615c3bdf52c291032144ce9e3b258a473c17c745047f3431ff8e2ee25f45bffff7f2000000000"), 5),
        'O': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066526f45bffff7f2001000000"), 6),
        'P': deserialize_header(bfh("00000020abe8e119d1877c9dc0dc502d1a253fb9a67967c57732d2f71ee0280e8381ff0a9690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe28126f45bffff7f2000000000"), 7),
        'Q': deserialize_header(bfh("000000202ce41d94eb70e1518bc1f72523f84a903f9705d967481e324876e1f8cf4d3452148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e1a126f45bffff7f2000000000"), 8),
        'R': deserialize_header(bfh("00000020552755b6c59f3d51e361d16281842a4e166007799665b5daed86a063dd89857415681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221a626f45bffff7f2000000000"), 9),
        'S': deserialize_header(bfh("00000020a13a491cbefc93cd1bb1938f19957e22a134faf14c7dee951c45533e2c750f239dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fab26f45bffff7f2000000000"), 10),
        'T': deserialize_header(bfh("00000020dbf3a9b55dfefbaf8b6e43a89cf833fa2e208bbc0c1c5d76c0d71b9e4a65337803b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064b026f45bffff7f2002000000"), 11),
        'U': deserialize_header(bfh("000000203d0932b3b0c78eccb39a595a28ae4a7c966388648d7783fd1305ec8d40d4fe5fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9db726f45bffff7f2001000000"), 12),
        'G': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066928f45bffff7f2001000000"), 6),
        'H': deserialize_header(bfh("00000020e19e687f6e7f83ca394c114144dbbbc4f3f9c9450f66331a125413702a2e1a719690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe26a28f45bffff7f2002000000"), 7),
        'I': deserialize_header(bfh("0000002009dcb3b158293c89d7cf7ceeb513add122ebc3880a850f47afbb2747f5e48c54148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e16a28f45bffff7f2000000000"), 8),
        'J': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221c928f45bffff7f2000000000"), 9),
        'K': deserialize_header(bfh("00000020bb3b421653548991998f96f8ba486b652fdb07ca16e9cee30ece033547cd1a6e9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fca28f45bffff7f2000000000"), 10),
        'L': deserialize_header(bfh("00000020c391d74d37c24a130f4bf4737932bdf9e206dd4fad22860ec5408978eb55d46303b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064ca28f45bffff7f2000000000"), 11),
        'M': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a4625558225522214229f45bffff7f2000000000"), 9),
        'N': deserialize_header(bfh("00000020383dab38b57f98aa9b4f0d5ff868bc674b4828d76766bf048296f4c45fff680a9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548f4329f45bffff7f2003000000"), 10),
        'X': deserialize_header(bfh("0000002067f1857f54b7fef732cb4940f7d1b339472b3514660711a820330fd09d8fba6b03b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe0649b29f45bffff7f2002000000"), 11),
        'Y': deserialize_header(bfh("00000020db33c9768a9e5f7c37d0f09aad88d48165946c87d08f7d63793f07b5c08c527fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9d9b29f45bffff7f2000000000"), 12),
        'Z': deserialize_header(bfh("0000002047822b67940e337fda38be6f13390b3596e4dea2549250256879722073824e7f0f2596c29203f8a0f71ae94193092dc8f113be3dbee4579f1e649fa3d6dcc38c622ef45bffff7f2003000000"), 13),
    }
    # tree of headers:
    #                                            - M <- N <- X <- Y <- Z
    #                                          /
    #                             - G <- H <- I <- J <- K <- L
    #                           /
    # A <- B <- C <- D <- E <- F <- O <- P <- Q <- R <- S <- T <- U

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        constants.set_regtest()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        constants.set_mainnet()

    def setUp(self):
        super().setUp()
        self.data_dir = self.electrum_path
        make_dir(os.path.join(self.data_dir, 'forks'))
        self.config = SimpleConfig({'electrum_path': self.data_dir})
        blockchain.blockchains = {}

    def _append_header(self, chain: Blockchain, header: dict):
        chain.save_header(header)

    def test_get_height_of_last_common_block_with_chain(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_parents_after_forking(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_forking_and_swapping(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])

        self._append_header(chain_l, self.HEADERS['K'])

        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

    def test_doing_multiple_swaps_after_single_new_header(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        # now chain_u is best chain, but it's tied with chain_l

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])


class TestVerifyHeader(ElectrumTestCase):

    # Data for Bitcoin block header #100.
    valid_header = "0100000095194b8567fe2e8bbda931afd01a7acd399b9325cb54683e64129bcd00000000660802c98f18fd34fd16d61c63cf447568370124ac5f3be626c2e1c3c9f0052d19a76949ffff001d33f3c25d"
    target = Blockchain.bits_to_target(0x1d00ffff)
    prev_hash = "00000000cd9b12643e6854cb25939b39cd7a1ad0af31a9bd8b2efe67854b1995"

    def setUp(self):
        super().setUp()
        self.header = deserialize_header(bfh(self.valid_header), 100)

    def test_valid_header(self):
        #Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_expected_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target,
        #                             expected_header_hash="foo")
        return

    def test_prev_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, "foo", self.target)
        return

    def test_target_mismatch(self):
        #with self.assertRaises(Exception):
        #    other_target = Blockchain.bits_to_target(0x1d00eeee)
        #    Blockchain.verify_header(self.header, self.prev_hash, other_target)
        return

    def test_insufficient_pow(self):
        #with self.assertRaises(Exception):
        #    self.header["nonce"] = 42
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_get_target(self):

        # before DGWv3 with checkpoint(height=2015)
        headers1 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2015, headers1)
        self.assertEqual(bits, 65339010432214603900175979833807329994044402934458085644623414103638016)

        # before DGWv3 without checkpoint(height=2016)
        headers2 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2016, headers2)
        self.assertEqual(bits, 0)

        # after DGWv3 with checkpoint(height=461663)
        headers3 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461663, headers3)
        self.assertEqual(bits, 62635231089126922960074598435273835921110428291665699134377033728)

        # after DGWv3 without checkpoint(height=461664)
        headers4 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461664, headers4)
        self.assertEqual(bits, 0)

        # after DGWv3 after checkpoint(1707577)
        headers5 = {1707552: {'version': 536870912, 'prev_block_hash': 'cbf4f8472308b332a146e224a029c8da8c247a5969d55120aeaebe09ddd3349d', 'merkle_root': 'e7072b993a857eac248968226de0442f653849b4e9e60389b1ff2f33a0198a6e', 'timestamp': 1562248741, 'bits': 438029645, 'nonce': 2789703934, 'block_height': 1707552}, 1707553: {'version': 536870912, 'prev_block_hash': '48ff72a7d036694e9ed274d213f9a2426a50467071df3feda04ab04ad8680cfe', 'merkle_root': '7a7ee20c7692dc24747543d03997c0bec5366dcdb9a94336144a236787ed2c04', 'timestamp': 1562248829, 'bits': 438095989, 'nonce': 3164952393, 'block_height': 1707553}, 1707554: {'version': 536870912, 'prev_block_hash': '5a96121d84a93d7552096aaac67915301cb436bb9ce573039095d5dd493b653e', 'merkle_root': '991e5bd597b65897c7f45d26416b61f8b14af8232c7a100fb114a8d0e89abbc9', 'timestamp': 1562248935, 'bits': 438157682, 'nonce': 1445694404, 'block_height': 1707554}, 1707555: {'version': 536870912, 'prev_block_hash': '422a5fe3981f83287c5a9b0dccf19cc70c4e67b01e36bb1477d651f94fc48f8b', 'merkle_root': 'a2f7addc721296d3ca3fa1818f919ef9764e9ca373e5c8433de84437eb6165de', 'timestamp': 1562248961, 'bits': 438157688, 'nonce': 1478829295, 'block_height': 1707555}, 1707556: {'version': 536870912, 'prev_block_hash': '584466ff1759343d10b78d0ab01e3629069ea7d10b89564b081e8d9ff5ff3c30', 'merkle_root': 'e321947646ac624c69f016d7230113770433ee428d42723d768eb7fa14d87e36', 'timestamp': 1562249235, 'bits': 437798855, 'nonce': 3758975225, 'block_height': 1707556}, 1707557: {'version': 536870912, 'prev_block_hash': '50b5ca95fcac67407dcde71ede2db3ef53b1d1344156a692db44c413d7312a4a', 'merkle_root': '1c145e28cd1a97ba5a3e49358ead6f11a9583f9cccc3a5da11213d9a6928e58c', 'timestamp': 1562249522, 'bits': 437953945, 'nonce': 1836890567, 'block_height': 1707557}, 1707558: {'version': 536870912, 'prev_block_hash': '1fca0a8366b93b1c008d63a331056cacb6cf7422620dbd4f2152db0231194015', 'merkle_root': '3888f38e1f8d355a23681510042a6b9c9da0f800bd1fe5d00d110360343b2992', 'timestamp': 1562249540, 'bits': 438060179, 'nonce': 4102151957, 'block_height': 1707558}, 1707559: {'version': 536870912, 'prev_block_hash': '8694453c547aac5d3cb3303a1ce113a80d05034ef441de49ebe0e5a50f1d089a', 'merkle_root': 'ddf7dfc4978dca3a9e81130348d8e488eeca1b8d400b025fc977df89e308b50a', 'timestamp': 1562249572, 'bits': 438068511, 'nonce': 4081611534, 'block_height': 1707559}, 1707560: {'version': 536870912, 'prev_block_hash': '010de19d9cf0f70e9c6bf8d81274d7bf083ee0f47e0dcc9a9339a3273cb0d8ff', 'merkle_root': '5eae451db7fa02b440d73505de56152f31f5b7691a385a1f9d43cc188196d72a', 'timestamp': 1562249587, 'bits': 438067280, 'nonce': 2683725381, 'block_height': 1707560}, 1707561: {'version': 536870912, 'prev_block_hash': 'c32967fb0ce200bcc7ad8c6776d1db76b89ac6b2638b2b93c0eb7147c93eabb1', 'merkle_root': 'b4fb627299b2898be36c20e7e1952e62c25c9a9ae91502b9f0c31f58dd5ef148', 'timestamp': 1562249642, 'bits': 438076949, 'nonce': 1851081340, 'block_height': 1707561}, 1707562: {'version': 536870912, 'prev_block_hash': '2b27d0a5a8907e8b4238e99bcc4c6181d41dd5991e34a48434ef3c41f7c74303', 'merkle_root': 'afc6babf8f3a9a4407efd8b35735d134afce2c1a05bc40e2f0cd7bbc0f2f9232', 'timestamp': 1562249744, 'bits': 438108094, 'nonce': 336655862, 'block_height': 1707562}, 1707563: {'version': 536870912, 'prev_block_hash': 'fcbddae87247934e8c5a37199e462aea5074649e64e52f510b006809b1ed4fba', 'merkle_root': 'e494390d0ec0c7667285561cb9a6f5fe33e962de95794c970ef2420a775d3002', 'timestamp': 1562249861, 'bits': 438168938, 'nonce': 821061911, 'block_height': 1707563}, 1707564: {'version': 536870912, 'prev_block_hash': 'a0a3313e2e27e6131b05fcbba565a346dda505272b24fc0d2af7cb01137c8bbc', 'merkle_root': '8497a0c7158c85fa2020a2d53d70f89f3feddc5b2fcc2e61b5cf6624940b1c2e', 'timestamp': 1562249982, 'bits': 438084687, 'nonce': 2147099528, 'block_height': 1707564}, 1707565: {'version': 536870912, 'prev_block_hash': '4b8425fdbb06945173be0cf489ee0b93c01f63cf0031bf5c8b80d54b85b650d4', 'merkle_root': '0ff67721536e3cda4927cfbfcc9479e33d5ea37d59b2ceb6238ca28730e5ac92', 'timestamp': 1562250002, 'bits': 438168583, 'nonce': 3843225892, 'block_height': 1707565}, 1707566: {'version': 536870912, 'prev_block_hash': '2397a2a53e95377393838f0fcc5e56058f67091f0f29f9052abd11cb08f8482d', 'merkle_root': '99d2149c54966f66204218e537da0ca37870405007d2beb76db4c65db2c506db', 'timestamp': 1562250012, 'bits': 438161036, 'nonce': 1959715855, 'block_height': 1707566}, 1707567: {'version': 536870912, 'prev_block_hash': 'bd9785c0b5064156b5b679f432d7094ba549669eb0621589114f073318b9f079', 'merkle_root': '841a902029ec01695a977a90fe18805fe595cc5b4fd99eb98d44113e7b615d2e', 'timestamp': 1562250094, 'bits': 438150641, 'nonce': 2029322498, 'block_height': 1707567}, 1707568: {'version': 536870912, 'prev_block_hash': '971559f276f5035ba270ddcc43a4577d01512b9e8f15c03ac4adb2ce2410cd3f', 'merkle_root': 'b2c37f344fe96d0f6e6a6fa3a76ae16a9a20d05b95dfde43f54da267f377086f', 'timestamp': 1562250273, 'bits': 438184125, 'nonce': 1309432981, 'block_height': 1707568}, 1707569: {'version': 536870912, 'prev_block_hash': '1a41cc2e2e3fff671ac76b4f3917bdad1173e9e95615b1157c058cf88c7901d8', 'merkle_root': '012a385ae807323c9b84841066572c5e12b7f449e354ba57c08e2a053d0da91e', 'timestamp': 1562250323, 'bits': 438331729, 'nonce': 2182159598, 'block_height': 1707569}, 1707570: {'version': 536870912, 'prev_block_hash': 'ea486c2cf14cfa12bbede9796e3f908840d95bbd76e2c22e9c39c7e8d0541c63', 'merkle_root': 'dfca511e854e1772183803186d65fa89635d61ee8eda778e9d6e9ee2d75d8db6', 'timestamp': 1562250360, 'bits': 438380359, 'nonce': 1378459661, 'block_height': 1707570}, 1707571: {'version': 536870912, 'prev_block_hash': '311f1543cde1d4d94e397369bb857839a68da7b5da220232a9e3e2778ff80fb6', 'merkle_root': '8043d19f3312e455413ed9926ff3c4b1e80322be5bb7cbfd7769ebb31910595d', 'timestamp': 1562250374, 'bits': 438375809, 'nonce': 1935902239, 'block_height': 1707571}, 1707572: {'version': 536870912, 'prev_block_hash': 'bd1a7c8d557195ccb51da479c8742fd45eed6343f19035dd88128b4c1fe837e9', 'merkle_root': 'c7128f5abfa5859b9045e86f2733e954e7e36e476e93a2e74f9cb4663c6e9179', 'timestamp': 1562250396, 'bits': 438299099, 'nonce': 141005783, 'block_height': 1707572}, 1707573: {'version': 536870912, 'prev_block_hash': '6c2628421ad9f65a3f5f534b9272003a68ae041909da7836561a6a405b92f16d', 'merkle_root': '528e348a05b0ad3847d3de2daef21925f74db3d537b118fa692e2e49c2f57c77', 'timestamp': 1562250490, 'bits': 437795403, 'nonce': 2301343266, 'block_height': 1707573}, 1707574: {'version': 536870912, 'prev_block_hash': '2fbf78a9bd6fecc27fab132c885da037355ffba8c29ae6fb666ecde4f8d2faa2', 'merkle_root': '415f0822a45f274c46bafc0a1a1536bdeb8b1c098ccf8055cc1e270dd28d35af', 'timestamp': 1562250959, 'bits': 437859823, 'nonce': 3905424503, 'block_height': 1707574}, 1707575: {'version': 536870912, 'prev_block_hash': '41e124c937a0923b80930f22580fb5b10c671588426bb9560798fa171747f75f', 'merkle_root': '1ef7fb4536283b8ec1f96c0de96933506e6727f31eda3fa4cc6672507d395cf4', 'timestamp': 1562251121, 'bits': 438247867, 'nonce': 980139439, 'block_height': 1707575}, 1707576: {'version': 536870912, 'prev_block_hash': '80bc982acc2fd07fda9eab66ff3bc4dda53832070cdfa4b39bab2f3323526d77', 'merkle_root': '1f92db8180b4902260f10f2b60bdd558036478fe7955af3ae60ec98ee74efb39', 'timestamp': 1562251156, 'bits': 438316136, 'nonce': 1154901627, 'block_height': 1707576}, 1707577: {'version': 536870912, 'prev_block_hash': '62aed78a2bba10217a30bd4343b6b1f0f7814d60c53011a2077bd8224d6c32e5', 'merkle_root': '06a42184dcb2378dd07eee92a9d27efb577bc690845cc483549a679edce3f7f2', 'timestamp': 1562251530, 'bits': 438284469, 'nonce': 2933328142, 'block_height': 1707577}}
        bits = Blockchain.get_target(self, 1707577, headers5)
        self.assertEqual(bits, 50924303622638816608903496611932117387916353275391498616157721)
