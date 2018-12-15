from __future__ import print_function
from Skeleton import MusicTheory
from Skeleton import Constants
from Arranging.Arranging import *
import InitializeSectionsHelper
import InitializeChordsAndPhraseHelper

import sys
import math
import random
import collections


class PianoSolo:

    def __init__(self, movement, selectedTempo):

        self.complexity = movement['complexity']
        self.durationInSecs = movement['duration']
        self.rhythmSpeed = movement['rhythmSpeed']
        self.selectedTempo = selectedTempo

        if (0):
            print("Mood: PianoSolo")
            print('Complexity: ', self.complexity)


        self.layers = {
            'leftPianoBass': {'density': 1, 'range': 'low', 'type': ''},

            'rightPiano': {'density': 1, 'range': 'mid', 'type': ''},

            'mel5': {'density': 1, 'range': 'all', 'type': ''},

            'piano1': {'density': 1, 'range': 'all', 'type': ''},
        }

        self.MaxAndMinLayersForEnergy = {
            'high'  : { 'max': 4,  'min': 3, 'initialMax': 2,  'initialMin': 1},
            'medium': { 'max': 3,   'min': 2, 'initialMax': 4,  'initialMin': 2},
            'low'   : { 'max': 2,   'min': 1, 'initialMax': 2,  'initialMin': 0},
        }

        self.arrange = Arranging("PianoSolo", self.layers, False)  # useDefault = False

        # set the initial phrase length
        if (movement['duration'] <= 45):
            self.possiblePLs = [2]
            self.primaryPL = random.choice(self.possiblePLs)
            self.numUniqCPs  = 1

        elif (movement['duration'] > 45 and movement['duration'] <= 90):
            self.possiblePLs = [4]
            self.primaryPL = random.choice(self.possiblePLs)
            self.numUniqCPs  = 2
        else:
            self.possiblePLs = [4, 4, 3, 4, 5]
            self.primaryPL = random.choice(self.possiblePLs)
            self.numUniqCPs  = random.choice([2, 3, 2])

        self.possiblePLs = [4]
        self.primaryPL = random.choice(self.possiblePLs)

        # set the initail BPM
        self.possibleBPMs = [x for x in range(84, 100, 1)]
        self.primaryBPM = random.choice(self.possibleBPMs)

        # set the initial scale
        self.possibleKeys = MusicTheory.AllKeys
        self.primaryScale = random.choice(self.possibleKeys)

        # set the initial TSE
        if (self.complexity == 'super_simple'):  # 95 % probability that tse remains same
            self.possibleTSEs = ['4/4']
            self.maxUniqCPs = 2
        elif (self.complexity == 'simple'):  # 95 % probability that tse remains same
            self.possibleTSEs = ['4/4']
            self.maxUniqCPs = 2
        elif (self.complexity == 'semi_complex'):  # 90 % probability that tse remains same
            self.possibleTSEs = ['3/4', '4/4', '5/4', '7/4', '3/8', '6/8', '7/8']
            random.shuffle(self.possibleTSEs)
            self.possibleTSEs = [self.possibleTSEs[0], self.possibleTSEs[1]]
            self.maxUniqCPs = 3
        elif (self.complexity == 'complex1'):  # 80 % probability that tse remains same
            self.possibleTSEs = ['4/4', '5/8', '6/8', '9/8', '11/8', '13/8', '3/16']
            random.shuffle(self.possibleTSEs)
            self.possibleTSEs = [self.possibleTSEs[0], self.possibleTSEs[1], self.possibleTSEs[2]]
            self.maxUniqCPs = 4

        self.primaryTSE = random.choice(self.possibleTSEs)

        self.minUniqCPs = len(movement['uniqTSEs'])
        self.minUniqCPs = 1
        self.maxUniqCPs = 7

        if (self.minUniqCPs > self.maxUniqCPs):
            self.maxUniqCPs = self.minUniqCPs

        self.uniqTSEIds = movement['uniqTSEs']

        if (1):
            print("TSE: ", self.primaryTSE)
            print("BPM: ", self.primaryBPM)
            print("KEY: ", self.primaryScale)
            print("PL : ", self.primaryPL)

            print("Number of UniqTSEs: ", len(movement['uniqTSEs']))
            print("XXX", self.uniqTSEIds)


        if (self.complexity.endswith('simple')):
            print(movement)
            self.InitializeMoodForSimple(movement['sectionSettings']);

    def InitializeMoodForSimple(self, sections):

        moodSpecificInfo = {'fills': False, 'numChords': self.primaryPL}
        self = InitializeSectionsHelper.InitializeSectionsComplex(self, sections, moodSpecificInfo)

        # sys.exit(0)
        self.keepHalfOfPrevLayers = True
        # self.keepHalfOfPrevLayers = False

        print(sections)
        self = InitializeChordsAndPhraseHelper.InitializeChordsAndPhraseForSections(self, sections)

        # sys.exit(0)

        if (1):
            print()
            print("Arrangement for Movement")
            for secId in self.sections:
                print("Section: ", secId, "Uniq Mel Id: ", self.sections[secId]['melId'], "startingMnum: ",
                      self.sections[secId]['startMNum'], "endMNum: ", self.sections[secId]['endMNum'], 'tse: ',
                      self.sections[secId]['tse'])
                uniqCPId = self.sections[secId]['melId']
                numChordsInPhrase = self.uniqCPSettings[uniqCPId]['numChords']
                phNum = 0
                for chId in self.sections[secId]['chords']:
                    if (chId % numChordsInPhrase == 0):
                        print("\tPhrase: ", phNum + 1, self.sections[secId]['phrases'][phNum])
                        phNum += 1
                    print("\t\tChord: ", chId, self.sections[secId]['chords'][chId])
                print()

    def setPercussionSettings(self, tse):

        type = 'defaultDrumKitSeparate'
        halfBeats = Constants.TSEBeatInfo[tse]['halfBeats']
        strongDownBeats = Constants.TSEBeatInfo[tse]['strongDownBeats']
        weakDownBeats = Constants.TSEBeatInfo[tse]['weakDownBeats']
        numBeats = Constants.TSEs[tse]['num16thBeats']
        oneExtra8thBeatForBassDrumsFilled = False

        BeatInfo = collections.OrderedDict()

        numBeats = Constants.TSEs[tse]['num16thBeats']
        eopStartBeat = numBeats + 1 - random.choice([numBeats // 2, numBeats // 4])  # end of phrase fill
        eosStartBeat = numBeats + 1 - random.choice(
            [numBeats, numBeats, numBeats, numBeats // 2, numBeats])  # end of section fill
        numPatterns = 1

        patterns = collections.OrderedDict()
        patterns[0] = {'eosStartBeat': eosStartBeat, 'eopStartBeat': eopStartBeat}

        if (0):
            print("eop: ", eopStartBeat, "eos: ", eosStartBeat)

        for i in range(1, numBeats + 1, 1):

            if (i in halfBeats):
                BeatInfo[i] = {
                    'kick': {'probMax': 90, 'probMin': 80, 'velocityMax': 120, 'velocityMin': 70},
                    'snare': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'hihat': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'bass': {'probMax': 80, 'probMin': 70, 'velocityMax': 120, 'velocityMin': 70},
                }

            elif (i in strongDownBeats):

                BeatInfo[i] = {
                    'kick': {'probMax': 90, 'probMin': 80, 'velocityMax': 120, 'velocityMin': 70},
                    'snare': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'hihat': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'bass': {'probMax': 50, 'probMin': 30, 'velocityMax': 120, 'velocityMin': 70},
                }


            elif (i in weakDownBeats):

                if (random.randint(0, 100) > 50) and not oneExtra8thBeatForBassDrumsFilled:
                    oneExtra8thBeatForBassDrumsFilled = True

                    BeatInfo[i] = {
                        'kick': {'probMax': 90, 'probMin': 80, 'velocityMax': 120, 'velocityMin': 70},
                        'snare': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                        'hihat': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                        'bass': {'probMax': 50, 'probMin': 30, 'velocityMax': 120, 'velocityMin': 70},
                    }

                else:  # this extra 8th beat was not chosen for bassdrum

                    BeatInfo[i] = {
                        'kick': {'probMax': 80, 'probMin': 70, 'velocityMax': 120, 'velocityMin': 70},
                        'snare': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                        'hihat': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                        'bass': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    }

            else:

                BeatInfo[i] = {
                    'kick': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'snare': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'hihat': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                    'bass': {'probMax': 0, 'probMin': 0, 'velocityMax': 0, 'velocityMin': 0},
                }

        return BeatInfo, patterns, type
