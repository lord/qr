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
# MAX_CHAR_COUNTS[error_level][version-1]
MAX_CHAR_COUNTS = {
	'L': [25, 47, 77, 114, 154,195, 224, 279, 335, 395],
	'M': [20, 38, 61, 90, 122, 154, 178, 221, 262, 311],
	'Q': [16, 29, 47, 67, 87, 108, 125, 157, 189,221],
	'H': [10, 20, 35, 50, 64, 84, 93, 122, 143, 174]
}

MODE_INDICATOR = '0010'

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

def get_version(msg_len, error_level="L"):
	version = 1
	while version <= 10 and MAX_CHAR_COUNTS[error_level][version-1] < msg_len:
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

def get_formatted_data(msg, version=1, error_level="L"):
	msg = msg.upper()
	char_count = format_char_count(len(msg), version=version)

	requiredWords = ERROR_CORRECTION_DICT[version][error_level]
	requiredBits = 8*requiredWords

	encodedMessage = encode_message(msg)
	terminalBits = min(4, requiredBits-len(encodedMessage))
	for bit in range(terminalBits):
		encodedMessage = str(encodedMessage)+str(0)

	temporaryString = MODE_INDICATOR+str(char_count)+str(encodedMessage)
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

	return_string = ""
	for i in range(len(temporaryString)):
		if i % 8 == 0:
			return_string = return_string+" "
		return_string = return_string+temporaryString[i]
	return return_string

BLOCKING_DICT = {
	'L':{1:([19],None), 2:([34],None), 3:([55],None), 4:([80],None), 5:([108],None), 6:([68, 68],None), 7:([78, 78],None), 8:([97, 97],None), 9:([116, 116],None), 10:([68, 68],[69, 69])},
	'M':{1:([16],None), 2:([28],None), 3:([44],None), 4:([32, 32],None), 5:([43, 43],None), 6:([27, 27, 27, 27],None), 7:([31, 31, 31, 31],None), 8:([38, 38],[39, 39]), 9:([36, 36, 36],[37, 37]), 10:([43, 43, 43, 43],[44])},
	'Q':{1:([13],None), 2:([22],None), 3:([17, 17],None), 4:([24, 24],None), 5:([15, 15],[16, 16]), 6:([19, 19, 19, 19],None), 7:([14, 14],[15, 15, 15, 15]), 8:([18, 18, 18, 18],[19, 19]), 9:([16, 16, 16, 16],[17, 17, 17, 17]), 10:([19, 19, 19, 19, 19, 19],[20, 20])},
	'H':{1:([9],None), 2:([16],None), 3:([13, 13],None), 4:([9, 9, 9, 9],None), 5:([11, 11],[12, 12]), 6:([15, 15, 15, 15],None), 7:([13, 13, 13, 13],[14]), 8:([14, 14, 14, 14],[15, 15]), 9:([12, 12, 12, 12],[13, 13, 13, 13]), 10:([15, 15, 15, 15, 15, 15],[16, 16])}
}
# returns list of groups [(num_blocks_in_group, num_codewords_per_block, ec)]
def get_blocking_counts(error_level="L", version=1):
	(g1, g2) = BLOCKING_DICT[error_level][version]
	if g2 == None:
		return [(len(g1), g1[0])]
	else:
		return [(len(g1), g1[0]), (len(g2), g2[0])]

# table of error correcting codewords per block for various versions and error levels
EC_TABLE = {'L':{1:7, 2:10, 3:15, 4:20, 5:26, 6:18, 7:20, 8:26, 9:30, 10:18},
'M':{1:10, 2:16, 3:26, 4:18, 5:24, 6:16, 7:18, 8:22, 9:22, 10:26},
'Q':{1:13, 2:22, 3:18, 4:26, 5:18, 6:24, 7:18, 8:22, 9:20, 10:24},
'H':{1:17, 2:28, 3:22, 4:16, 5:22, 6:28, 7:26, 8:26, 9:24, 10:28}}

def error_correction(encoded_msg, error_level="L", version=1):
	error_cw_per_block = EC_TABLE[error_level][version]
	gen_poly_template = find_generator_poly(error_cw_per_block)
	group_blockings = get_blocking_counts(error_level=error_level, version=version)
	msg_poly = list(filter(len, encoded_msg.split(" "))) # filter out empty strings

	# convert each binary string into a number, which become coefficients of the gen polynomial
	msg_poly = list(map(lambda i: int(i,2), msg_poly))

	group_data = []
	group_err = []
	for (num_blocks, codewords_per_block) in group_blockings:
		# pull numbers from global message polynomial into groupings
		blocks = []
		for block_num in range(num_blocks):
			block_data = []
			for codeword_num in range(codewords_per_block):
				block_data.append(msg_poly[block_num*codewords_per_block + codeword_num])
			blocks.append(block_data)
		group_data.append(blocks)

		# multiply gen poly so degree is same as eventual error correction poly

		err_codewords = []
		for block in blocks:
			# copy block into result polynomial, multiply by number of error codewords per block so that
			# the lead term's exponent doesn't run out during divison
			# this is called the message polynomial too, but it has this nameh to distinguish from the
			# global msg_poly
			result_poly = block[:]
			for _ in range(error_cw_per_block):
				result_poly.append(0)

			# division loop: number of division steps is equal to number of terms in message polynomial
			for j in range(codewords_per_block):

				# copy gen poly base, multiply so degree is same as result poly
				gen_poly = gen_poly_template[:]
				while len(gen_poly) < len(result_poly):
					gen_poly.append(0)

				# multiply generator poly by lead term of of msg poly
				for i in range(len(gen_poly)):
					gen_poly[i] = field_mult(result_poly[0], gen_poly[i])

				# xor result with msg polynomial
				for i in range(len(result_poly)):
					result_poly[i] = gen_poly[i]^result_poly[i]

				# slice away the now-zero leading term
				result_poly = result_poly[1:]

			err_codewords.append(result_poly)
		group_err.append(err_codewords)

	for a in [group_data, group_err]:
		for b in a:
			for c in b:
				for i in range(len(c)):
					c[i] = bin(c[i])[2:].zfill(8)

	max_data_cw = max(map(lambda i: i[1], group_blockings))
	max_group = group_blockings[0][0]
	interleaved_msg = ""
	interleaved_err = ""
	for j in range(max_data_cw):
		for i in range(max_group):
			for group in group_data:
				if i < len(group) and j < len(group[i]):
					interleaved_msg += str(group[i][j])

	for j in range(error_cw_per_block):
		for i in range(max_group):
			for group in group_err:
				if i < len(group) and j < len(group[i]):
					interleaved_err += str(group[i][j])

	finalMessage = interleaved_msg+interleaved_err
	remainderBits = [0, 7, 7, 7, 7, 7, 0, 0, 0, 0]
	numRemainderBits = remainderBits[version - 1]
	for bit in range(numRemainderBits):
		finalMessage = finalMessage + str(0)

	return finalMessage

# Alpha-to-int
AI = [
  1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38,
  76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96,
  192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238,
  193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210,
  185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202,
  137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127,
  254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34,
  68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124,
  248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23,
  46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168,
  77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183,
  115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123,
  246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110,
  220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56,
  112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239,
  195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244,
  245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250,
  233, 207, 131, 27, 54, 108, 216, 173, 71, 142
]

# multiple two numbers in the bitwise field
def field_mult(a, b):
	if a == 0 or b == 0:
		return 0
	a_alpha = AI.index(a)
	b_alpha = AI.index(b)
	res_alpha = (a_alpha + b_alpha) % 255
	return AI[res_alpha]

def find_generator_poly(numberECWords):
	# if numberECWords == 7:
	# 	return [2**0, 2**87, 2**229, 2**146, 2**149, 2**238, 2**102, 2**21]
	# else:
	# 	previousPoly = self.find_generator_poly(numberECWords - 1)
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
	generatorPolynomials = {
		7: [AI[0], AI[87], AI[229], AI[147], AI[149], AI[238], AI[102], AI[21]],
		8: [AI[0], AI[175], AI[238], AI[208], AI[249], AI[215], AI[252], AI[196], AI[28]],
		9: [AI[0], AI[95], AI[246], AI[137], AI[231], AI[235], AI[149], AI[11], AI[123], AI[36]],
		10: [AI[0], AI[251], AI[67], AI[46], AI[61], AI[118], AI[70], AI[64], AI[94], AI[32], AI[45]],
		11: [AI[0], AI[220], AI[192], AI[91], AI[194], AI[172], AI[177], AI[209], AI[116], AI[227], AI[10], AI[55]],
		12: [AI[0], AI[102], AI[43], AI[98], AI[121], AI[187], AI[113], AI[198], AI[143], AI[131], AI[87], AI[157], AI[66]],
		13: [AI[0], AI[74], AI[152], AI[176], AI[100], AI[86], AI[100], AI[106], AI[104], AI[130], AI[218], AI[206], AI[140], AI[78]],
		14: [AI[0], AI[199], AI[249], AI[155], AI[48], AI[190], AI[124], AI[218], AI[137], AI[216], AI[87], AI[207], AI[59], AI[22], AI[91]],
		15: [AI[0], AI[8], AI[183], AI[61], AI[91], AI[202], AI[37], AI[51], AI[58], AI[58], AI[237], AI[140], AI[124], AI[5], AI[99], AI[105]],
		16: [AI[0], AI[120], AI[104], AI[107], AI[109], AI[102], AI[161], AI[76], AI[3], AI[191], AI[147], AI[169], AI[182], AI[194], AI[225], AI[120]],
		17: [AI[0], AI[43], AI[139], AI[206], AI[78], AI[43], AI[239], AI[123], AI[206], AI[214], AI[147], AI[24], AI[99], AI[150], AI[39], AI[243], AI[163], AI[136]],
		18: [AI[0], AI[215], AI[234], AI[158], AI[94], AI[184], AI[97], AI[118], AI[170], AI[79], AI[187], AI[152], AI[148], AI[252], AI[179], AI[5], AI[98], AI[96], AI[153]],
		19: [AI[0], AI[57], AI[3], AI[105], AI[153], AI[52], AI[90], AI[83], AI[17], AI[150], AI[159], AI[44], AI[128], AI[153], AI[133], AI[252], AI[222], AI[138], AI[220], AI[171]],
		20: [AI[0], AI[17], AI[60], AI[79], AI[50], AI[61], AI[163], AI[26], AI[187], AI[202], AI[180], AI[221], AI[225], AI[83], AI[239], AI[156], AI[164], AI[212], AI[212], AI[188], AI[190]],
		21: [AI[0], AI[240], AI[233], AI[104], AI[247], AI[181], AI[140], AI[67], AI[98], AI[85], AI[200], AI[210], AI[115], AI[148], AI[137], AI[230], AI[36], AI[122], AI[254], AI[148], AI[175], AI[210]],
		22: [AI[0], AI[210], AI[171], AI[247], AI[242], AI[93], AI[230], AI[14], AI[109], AI[221], AI[53], AI[200], AI[74], AI[8], AI[172], AI[98], AI[80], AI[219], AI[134], AI[160], AI[105], AI[165], AI[231]],
		23: [AI[0], AI[171], AI[102], AI[146], AI[91], AI[49], AI[103], AI[65], AI[17], AI[193], AI[150], AI[14], AI[25], AI[183], AI[248], AI[94], AI[164], AI[224], AI[192], AI[1], AI[78], AI[56], AI[147], AI[253]],
		24: [AI[0], AI[229], AI[121], AI[135], AI[48], AI[211], AI[117], AI[251], AI[126], AI[159], AI[180], AI[169], AI[152], AI[192], AI[226], AI[228], AI[218], AI[111], AI[0], AI[117], AI[232], AI[87], AI[96], AI[227], AI[21]],
		25: [AI[0], AI[231], AI[181], AI[156], AI[39], AI[170], AI[26], AI[12], AI[59], 215, AI[148], AI[201], AI[54], AI[66], AI[237], AI[208], AI[99], AI[167], AI[144], AI[182], AI[95], AI[243], AI[129], AI[178], AI[252], AI[45]],
		26: [AI[0], AI[173], AI[125], AI[158], AI[2], AI[103], AI[182], AI[118], AI[17], AI[145], AI[201], AI[111], AI[28], AI[165], AI[53], AI[161], AI[21], AI[245], AI[142], AI[13], AI[102], AI[48], AI[227], AI[153], AI[145], AI[218], AI[70]],
		27: [AI[0], AI[79], AI[228], AI[8], AI[165], AI[227], AI[21], AI[180], AI[29], AI[9], AI[237], AI[70], AI[99], AI[45], AI[58], AI[138], AI[135], AI[73], AI[126], AI[172], AI[94], AI[216], AI[193], AI[157], AI[26], AI[17], AI[149], AI[96]],
		28: [AI[0], AI[168], AI[223], AI[200], AI[104], AI[224], AI[234], AI[108], AI[180], AI[110], AI[190], AI[195], AI[147], AI[205], AI[27], AI[232], AI[201], AI[21], AI[43], AI[245], AI[87], AI[42], AI[195], AI[212], AI[119], AI[242], AI[37], AI[9], AI[123]]
	}

	return generatorPolynomials[numberECWords]

def get_qr(msg, error_level='M'):
	version = get_version(len(msg), error_level=error_level)
	encoded_msg = get_formatted_data(msg, version=version, error_level=error_level)
	fullyEncodedMessage = error_correction(encoded_msg, version=version, error_level=error_level)
	return fullyEncodedMessage

def main():
	# parser = argparse.ArgumentParser(description='Provide an alphanumeric string and error correction level.')
	# parser.add_argument('message', metavar='N', type=str, nargs='+',
 #       help='a message to encode')
	# parser.add_argument('errorLevel', type=str, default='Q',
 #        help='Error correction level: \'L\', \'M\', \'Q\', or \'H\'.  Default: \'Q\'')

	# args = parser.parse_args()
	# args[0] = message
	# args[1] = errorLevel
	print(get_qr('hello world', error_level='Q'))

if __name__ == "__main__":
	main()