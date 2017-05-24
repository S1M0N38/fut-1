#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for fut.core"""

import unittest
import responses
import re
import json
from sys import path

from fut import core
from fut.urls import urls
from fut.exceptions import FutError


class FutCoreTestCase(unittest.TestCase):

    # _multiprocess_can_split_ = True

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEntryPoints(self):
        core.Core

    def testBaseId(self):
        # TODO: 3x test for every version
        self.assertEqual(core.baseId(124635), 124635)
        self.assertEqual(core.baseId(124635, return_version=True), (124635, 0))
        self.assertEqual(core.baseId(149147, return_version=True), (149147, 0))
        self.assertEqual(core.baseId(222492, return_version=True), (222492, 0))
        self.assertEqual(core.baseId(50510135, return_version=True), (178487, 3))
        self.assertEqual(core.baseId(50556989, return_version=True), (225341, 3))
        self.assertEqual(core.baseId(50562314, return_version=True), (230666, 3))
        self.assertEqual(core.baseId(67340541, return_version=True), (231677, 4))
        self.assertEqual(core.baseId(67319481, return_version=True), (210617, 4))
        self.assertEqual(core.baseId(84072233, return_version=True), (186153, 5))

    @responses.activate
    def testDatabase(self):
        responses.add(responses.GET,
                      urls('pc')['messages'],
                      body=open(path[0] + '/tests/data/messages.en_US.xml', 'r').read())
        responses.add(responses.GET,
                      '{0}{1}.json'.format(urls('pc')['card_info'], 'players'),
                      json=json.loads(open(path[0] + '/tests/data/players.json', 'r').read()))  # load json to avoid encoding errors

        self.db_nations = core.nations()
        self.db_leagues = core.leagues()
        self.db_teams = core.teams()
        self.db_players = core.players()

        # TODO: drop re, use xmltodict
        # TODO: year in config
        year = 2017
        rc = open(path[0] + '/tests/data/messages.en_US.xml', 'r').read()
        for i in re.findall('<trans-unit resname="search.nationName.nation([0-9]+)">\n        <source>(.+)</source>', rc[:]):
            self.assertEqual(self.db_nations[int(i[0])], i[1])

        for i in re.findall('<trans-unit resname="global.leagueFull.%s.league([0-9]+)">\n        <source>(.+)</source>' % year, rc[:]):
            self.assertEqual(self.db_leagues[int(i[0])], i[1])

        for i in re.findall('<trans-unit resname="global.teamFull.%steam([0-9]+)">\n        <source>(.+)</source>' % year, rc[:]):
            self.assertEqual(self.db_teams[int(i[0])], i[1])

        rc = json.loads(open(path[0] + '/tests/data/players.json', 'r').read())
        for i in rc['Players'] + rc['LegendsPlayers']:
            self.assertEqual(self.db_players[i['id']],
                             {'id': i['id'],
                              'firstname': i['f'],
                              'lastname': i['l'],
                              'surname': i.get('c'),
                              'rating': i['r'],
                              'nationality': i['n']})

    def testInvalidAccount(self):
        #  TODO: responses
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', debug=True)
        # platforms
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', platform='xbox', debug=True)
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', platform='xbox360', debug=True)
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', platform='ps3', debug=True)
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', platform='ps4', debug=True)
        # emulate
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', emulate='ios', debug=True)
        self.assertRaises(FutError, core.Core, 'test', 'test', 'test', emulate='and', debug=True)


if __name__ == '__main__':
    unittest.main()
