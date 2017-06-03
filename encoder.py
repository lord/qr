import argparse
import math
import copy

# a dictionary specifying required codeword counts. Ordered by version:correction:codewords
ERROR_CORRECTION_DICT = {
	1:{'L':19,'M':16,'Q':13,'H':9},
	2:{'L':34, 'M':28, 'Q':22, 'H':16},
	3:{'L':55, 'M':44, 'Q':34, 'H':26},
	4:{'L':80, 'M':64, 'Q':48, 'H':36},
	5:{'L':108, 'M':86, 'Q':62, 'H':46},
	6:{'L':136, 'M':108, 'Q':76, 'H':60},
	7:{'L':156, 'M':124, 'Q':88, 'H':66},
	8:{'L':194, 'M':154, 'Q':110, 'H':86},
	9:{'L':232, 'M':182, 'Q':132, 'H':100},
	10:{'L':274, 'M':216, 'Q':154, 'H':122}
}

# maximum character counts are stored as a dict
# MAX_CHAR_COUNTS[correction_level][version-1]
MAX_CHAR_COUNTS = {
	'L': [25, 47, 77, 114, 154,195, 224, 279, 335, 395],
	'M': [20, 38, 61, 90, 122, 154, 178, 221, 262, 311],
	'Q': [16, 29, 47, 67, 87, 108, 125, 157, 189,221],
	'H': [10, 20, 35, 50, 64, 84, 93, 122, 143, 174]
}

def encode_message(msg):
	alphanumericValueTable = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D',
		'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
		'V', 'W', 'X', 'Y', 'Z', ' ', '$', '%', '*', '+', '-', '.', '/', ':']
	messageEncoding = ""
	for i in range(len(msg)//2):
		firstValue = 45 * alphanumericValueTable.index(msg[2*i])
		secondValue = alphanumericValueTable.index(msg[2*i+1])
		value = firstValue+secondValue
		binaryValue = bin(value)[2:].zfill(8)
		paddingBits = 11 - len(binaryValue)
		for bit in range(paddingBits):
			binaryValue = str(0)+str(binaryValue)
		messageEncoding = messageEncoding + str(binaryValue)
	if (len(msg) % 2 != 0):
		lastValue = alphanumericValueTable.index(msg[-1])
		binaryValue = bin(lastValue)[2:]
		paddingBits = 6 - len(binaryValue)
		for bit in range(paddingBits):
			binaryValue = str(0)+str(binaryValue)
		messageEncoding = messageEncoding + str(binaryValue)
	return messageEncoding

def get_version(correction_level, message_length):
	version = 1
	while version <= 10 and MAX_CHAR_COUNTS[correction_level][version-1] < message_length:
		version += 1
	if version > 10:
		raise RuntimeError("message is too long for largest supported version size!")
	return version

def format_char_count(msg_len, version=1):
	if version == 10:
		indicatorSize = 11
	else:
		indicatorSize = 9
	messageLengthBinary = bin(msg_len)[2:].zfill(8)
	paddingBits = indicatorSize - len(messageLengthBinary)
	charCountValue=""
	for bit in range(paddingBits):
		charCountValue = str(0)+str(charCountValue)
	charCountValue = charCountValue + messageLengthBinary
	return charCountValue

class Encoder:
	def __init__(self, messageString, errorCorrection):
		self.originalData = messageString
		self.charCount = 0
		self.modeIndicator = '0010'
		self.dataEncoding = ''
		self.returnString = ''
		self.correctionLevel = errorCorrection
		self.version = 1

	def formatReturnString(self):
		requiredWords = ERROR_CORRECTION_DICT[self.version][self.correctionLevel]
		requiredBits = 8*requiredWords

		encodedMessage = encode_message(self.originalData)
		terminalBits = min(4, requiredBits-len(encodedMessage))
		for bit in range(terminalBits):
			encodedMessage = str(encodedMessage)+str(0)
		self.dataEncoding = encodedMessage

		self.version = get_version(self.correctionLevel, len(self.originalData))
		self.charCount = format_char_count(len(self.originalData), version=self.version)

		temporaryString = self.modeIndicator+str(self.charCount)+str(self.dataEncoding)
		while not (len(temporaryString) % 8 == 0):
			temporaryString = temporaryString + str(0)
		if (len(temporaryString) != requiredBits):
			extraBitsNeeded = requiredBits - len(temporaryString)
			padBytesNeeded = int(extraBitsNeeded / 8)

			temporaryString
			for i in range(padBytesNeeded):
				if (i % 2) == 0:
					temporaryString = temporaryString + '11101100'
				else:
					temporaryString = temporaryString + '00010001'
		for i in range(len(temporaryString)):
			if i % 8 == 0:
				self.returnString = self.returnString+" "
			self.returnString = self.returnString+temporaryString[i]
		return self.returnString

	def errorCorrection(self, messageString):
		ECTable = {'L':{1:7, 2:10, 3:15, 4:20, 5:26, 6:18, 7:20, 8:26, 9:30, 10:18},
		'M':{1:10, 2:16, 3:26, 4:18, 5:24, 6:16, 7:18, 8:22, 9:22, 10:26},
		'Q':{1:13, 2:22, 3:18, 4:26, 5:18, 6:24, 7:18, 8:22, 9:20, 10:24},
		'H':{1:17, 2:28, 3:22, 4:16, 5:22, 6:28, 7:26, 8:26, 9:24, 10:28}}
		errorCorrectionPerBlock = ECTable[self.correctionLevel][self.version]
		blockingDictionary = {'L':{1:[[19],[]], 2:[[34],[]], 3:[[55],[]], 4:[[80],[]], 5:[[108],[]], 6:[[68, 68],[]], 7:[[78, 78],[]], 8:[[97, 97],[]], 9:[[116, 116],[]], 10:[[68, 68],[69, 69]]},
		'M':{1:[[16],[]], 2:[[28],[]], 3:[[44],[]], 4:[[32, 32],[]], 5:[[43, 43],[]], 6:[[27, 27, 27, 27],[]], 7:[[31, 31, 31, 31],[]], 8:[[38, 38],[39, 39]], 9:[[36, 36, 36],[37, 37]], 10:[[43, 43, 43, 43],[44]]},
		'Q':{1:[[13],[]], 2:[[22],[]], 3:[[17, 17],[]], 4:[[24, 24],[]], 5:[[15, 15],[16, 16]], 6:[[19, 19, 19, 19],[]], 7:[[14, 14],[15, 15, 15, 15]], 8:[[18, 18, 18, 18],[19, 19]], 9:[[16, 16, 16, 16],[17, 17, 17, 17]], 10:[[19, 19, 19, 19, 19, 19],[20, 20]]},
		'H':{1:[[9],[]], 2:[[16],[]], 3:[[13, 13],[]], 4:[[9, 9, 9, 9],[]], 5:[[11, 11],[12, 12]], 6:[[15, 15, 15, 15],[]], 7:[[13, 13, 13, 13],[14]], 8:[[14, 14, 14, 14],[15, 15]], 9:[[12, 12, 12, 12],[13, 13, 13, 13]], 10:[[15, 15, 15, 15, 15, 15],[16, 16]]}}
		numGroupOneBlocks = len(blockingDictionary[self.correctionLevel][self.version][0])
		numDataCodewordsGroupOne = blockingDictionary[self.correctionLevel][self.version][0][0]
		numGroupTwoBlocks = len(blockingDictionary[self.correctionLevel][self.version][1])
		if numGroupTwoBlocks > 0:
			numDataCodewordsGroupTwo = blockingDictionary[self.correctionLevel][self.version][1][0]
		else:
			numDataCodewordsGroupTwo = 0
		messagePolynomial = messageString.split(" ")
		if (messagePolynomial[0] == ""):
			messagePolynomial = messagePolynomial[1:]

		for coefficient in messagePolynomial:

			coefficient = int(coefficient, 2)
		groupOne = []
		groupTwo = []
		for block in range(numGroupOneBlocks):
			dataCodewordsBlock = []
			for codeword in range(numDataCodewordsGroupOne):
				dataCodewordsBlock.append(messagePolynomial[block*numDataCodewordsGroupOne + codeword])
			groupOne.append(dataCodewordsBlock)
		for block in range(numGroupTwoBlocks):
			dataCodewordsBlock = []
			for codeword in range(0, numDataCodewordsGroupTwo):
				dataCodewordsBlock.append(messagePolynomial[block*numDataCodewordsGroupTwo + codeword])
			groupTwo.append(dataCodewordsBlock)

		generatorPolynomial = self.generatorPolynomialFinder(errorCorrectionPerBlock)
		generatorPolyOne = copy.copy(generatorPolynomial)
		for word in range(numDataCodewordsGroupOne):
			generatorPolyOne.append(0)
		generatorMultPolyOne = copy.copy(generatorPolyOne)

		generatorPolyTwo = copy.copy(generatorPolynomial)
		for word in range(numDataCodewordsGroupTwo):
			generatorPolyTwo.append(0)
		generatorMultPolyTwo = copy.copy(generatorPolyTwo)


		groupOneErrorCorrection = []
		i = 0
		while(i < len(groupOne)):
			resultPoly = copy.copy(groupOne[i])
			for error in range(errorCorrectionPerBlock):
				resultPoly.append(0)
			for i in range(numDataCodewordsGroupOne):
				for j in range(0, len(generatorPolyOne)):
					generatorMultPolyOne[j] = int(resultPoly[0])*generatorPolyOne[j]
				for k in range(0, len(messagePolynomial)):
					resultPoly[k] = int(generatorMultPolyOne[k])^int(resultPoly[k])
			for term in resultPoly:
				term = bin(term)
			groupOneErrorCorrection.append(resultPoly)


		groupTwoErrorCorrection = []
		i = 0
		while(i < len(groupTwo)):
			resultPoly = copy.copy(groupTwo[i])
			for error in range(errorCorrectionPerBlock):
				resultPoly.append(0)
			for i in range(numDataCodewordsGroupTwo):
				for j in range(len(generatorPolyTwo)):
					generatorMultPolyTwo[j] = resultPoly[0]*generatorPolyTwo[j]
				for k in range(len(messagePolynomial)):
					resultPoly[k] = generatorMultPolyTwo[k]^resultPoly[k]
			for term in resultPoly:
				term = bin(term)
			groupTwoErrorCorrection.append(resultPoly)


		sizeLimit = max(numDataCodewordsGroupTwo, numDataCodewordsGroupOne)
		interleavedMessage = ""
		interleavedEC = ""
		for j in range(sizeLimit):
			for i in range(numGroupOneBlocks):
				if (j < numDataCodewordsGroupOne):
					interleavedMessage = interleavedMessage+str(groupOne[i][j])

				if (j < numDataCodewordsGroupTwo and i < numGroupTwoBlocks):
					interleavedMessage = interleavedMessage+str(groupTwo[i][j])

		for j in range(errorCorrectionPerBlock):
			for i in range(numGroupOneBlocks):
				interleavedEC = interleavedEC+str(groupOneErrorCorrection[i][j])
				if i<numGroupTwoBlocks:
					interleavedEC = interleavedEC+str(groupTwoErrorCorrection[i][j])

		finalMessage = interleavedMessage+interleavedEC
		remainderBits = [0, 7, 7, 7, 7, 7, 0, 0, 0, 0]
		numRemainderBits = remainderBits[self.version - 1]
		for bit in range(numRemainderBits):
			finalMessage = finalMessage +str(0)

		return finalMessage


	def generatorPolynomialFinder(self, numberECWords):
		# if numberECWords == 7:
		# 	return [2**0, 2**87, 2**229, 2**146, 2**149, 2**238, 2**102, 2**21]
		# else:
		# 	previousPoly = self.generatorPolynomialFinder(numberECWords - 1)
		# 	multPoly = [1, 2**(numberECWords-1)]
		# 	returnPoly = []
		# 	for term in range(numberECWords):
		# 		returnPoly.append(0)
		# 	for i in range(len(previousPoly)):
		# 		for j in range(2):
		# 			prevPolyExp = math.log(previousPoly[i], 2)
		# 			multPolyExp = math.log(multPoly[j], 2)
		# 			resultExp = ((prevPolyExp+multPolyExp)%256)+math.floor((prevPolyExp+multPolyExp/256))
		# 			returnPoly[i+j] = returnPoly[i+j]^int((2**resultExp))
		# 	return returnPoly
		generatorPolynomials = {7: [2**0, 2**87, 2**229, 2**147, 2**149, 2**238, 2**102, 2**21],
		8: [2**0, 2**175, 2**238, 2**208, 2**249, 2**215, 2**252, 2**196, 2**28],
		9: [2**0, 2**95, 2**246, 2**137, 2**231, 2**235, 2**149, 2**11, 2**123, 2**36],
		10: [2**0, 2**251, 2**67, 2**46, 2**61, 2**118, 2**70, 2**64, 2**94, 2**32, 2**45],
		11: [2**0, 2**220, 2**192, 2**91, 2**194, 2**172, 2**177, 2**209, 2**116, 2**227, 2**10, 2**55],
		12: [2**0, 2**102, 2**43, 2**98, 2**121, 2**187, 2**113, 2**198, 2**143, 2**131, 2**87, 2**157, 2**66],
		13: [2**0, 2**74, 2**152, 2**176, 2**100, 2**86, 2**100, 2**106, 2**104, 2**130, 2**218, 2**206, 2**140, 2**78],
		14: [2**0, 2**199, 2**249, 2**155, 2**48, 2**190, 2**124, 2**218, 2**137, 2**216, 2**87, 2**207, 2**59, 2**22, 2**91],
		15: [2**0, 2**8, 2**183, 2**61, 2**91, 2**202, 2**37, 2**51, 2**58, 2**58, 2**237, 2**140, 2**124, 2**5, 2**99, 2**105],
		16: [2**0, 2**120, 2**104, 2**107, 2**109, 2**102, 2**161, 2**76, 2**3, 2**191, 2**147, 2**169, 2**182, 2**194, 2**225, 2**120],
		17: [2**0, 2**43, 2**139, 2**206, 2**78, 2**43, 2**239, 2**123, 2**206, 2**214, 2**147, 2**24, 2**99, 2**150, 2**39, 2**243, 2**163, 2**136],
		18: [2**0, 2**215, 2**234, 2**158, 2**94, 2**184, 2**97, 2**118, 2**170, 2**79, 2**187, 2**152, 2**148, 2**252, 2**179, 2**5, 2**98, 2**96, 2**153],
		19: [2**0, 2**57, 2**3, 2**105, 2**153, 2**52, 2**90, 2**83, 2**17, 2**150, 2**159, 2**44, 2**128, 2**153, 2**133, 2**252, 2**222, 2**138, 2**220, 2**171],
		20: [2**0, 2**17, 2**60, 2**79, 2**50, 2**61, 2**163, 2**26, 2**187, 2**202, 2**180, 2**221, 2**225, 2**83, 2**239, 2**156, 2**164, 2**212, 2**212, 2**188, 2**190],
		21: [2**0, 2**240, 2**233, 2**104, 2**247, 2**181, 2**140, 2**67, 2**98, 2**85, 2**200, 2**210, 2**115, 2**148, 2**137, 2**230, 2**36, 2**122, 2**254, 2**148, 2**175, 2**210],
		22: [2**0, 2**210, 2**171, 2**247, 2**242, 2**93, 2**230, 2**14, 2**109, 2**221, 2**53, 2**200, 2**74, 2**8, 2**172, 2**98, 2**80, 2**219, 2**134, 2**160, 2**105, 2**165, 2**231],
		23: [2**0, 2**171, 2**102, 2**146, 2**91, 2**49, 2**103, 2**65, 2**17, 2**193, 2**150, 2**14, 2**25, 2**183, 2**248, 2**94, 2**164, 2**224, 2**192, 2**1, 2**78, 2**56, 2**147, 2**253],
		24: [2**0, 2**229, 2**121, 2**135, 2**48, 2**211, 2**117, 2**251, 2**126, 2**159, 2**180, 2**169, 2**152, 2**192, 2**226, 2**228, 2**218, 2**111, 2**0, 2**117, 2**232, 2**87, 2**96, 2**227, 2**21],
		25: [2**0, 2**231, 2**181, 2**156, 2**39, 2**170, 2**26, 2**12, 2**59, 215, 2**148, 2**201, 2**54, 2**66, 2**237, 2**208, 2**99, 2**167, 2**144, 2**182, 2**95, 2**243, 2**129, 2**178, 2**252, 2**45],
		26: [2**0, 2**173, 2**125, 2**158, 2**2, 2**103, 2**182, 2**118, 2**17, 2**145, 2**201, 2**111, 2**28, 2**165, 2**53, 2**161, 2**21, 2**245, 22**142, 2**13, 2**102, 2**48, 2**227, 2**153, 2**145, 2**218, 2**70],
		27: [2**0, 2**79, 2**228, 2**8, 2**165, 2**227, 2**21, 2**180, 2**29, 2**9, 2**237, 2**70, 2**99, 2**45, 2**58, 2**138, 2**135, 2**73, 2**126, 2**172, 2**94, 2**216, 2**193, 2**157, 2**26, 2**17, 2**149, 2**96],
		28: [2**0, 2**168, 2**223, 2**200, 2**104, 2**224, 2**234, 2**108, 2**180, 2**110, 2**190, 2**195, 2**147, 2**205, 2**27, 2**232, 2**201, 2**21, 2**43, 2**245, 2**87, 2**42, 2**195, 2**212, 2**119, 2**242, 2**37, 2**9, 2**123]
		}

		return generatorPolynomials[numberECWords]

def main():
	# parser = argparse.ArgumentParser(description='Provide an alphanumeric string and error correction level.')
	# parser.add_argument('message', metavar='N', type=str, nargs='+',
 #       help='a message to encode')
	# parser.add_argument('errorLevel', type=str, default='Q',
 #        help='Error correction level: \'L\', \'M\', \'Q\', or \'H\'.  Default: \'Q\'')

	# args = parser.parse_args()
	# args[0] = message
	# args[1] = errorLevel
	message = 'hello world'
	errorLevel = 'M'
	message = message.upper()
	stringEncoder = Encoder(message, errorLevel)
	encodedMessage = stringEncoder.formatReturnString()
	fullyEncodedMessage = stringEncoder.errorCorrection(encodedMessage)

	print(fullyEncodedMessage)

if __name__ == "__main__":
	main()