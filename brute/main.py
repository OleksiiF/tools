import subprocess
import itertools
import string


class Brute:
	def __init__(
		self,
		target: str,
		min_length=1,
		max_length=10,
		upper=True,
		lower=True,
		digits=True,
		special=True,
		vocabulary=''
	):
		self.vocabulary: str = vocabulary
		self.password = None
		self.target: str = target
		self.file_extension: str = target.split('.')[-1]
		self.min_length: int = min_length
		self.max_length: int = max_length
		self.upper: str = string.ascii_uppercase if upper else ''
		self.lower: str = string.ascii_lowercase if lower else ''
		self.digits: str = string.digits if digits else ''
		self.special: str = string.punctuation if special else ''

	def _get_from_vocabulary(self):
		with open(self.vocabulary) as fh:
			for line in fh:
				yield line

	def _get_from_generator(self):
		for word_length in range(self.min_length, self.max_length):
			for word in itertools.permutations(
				self.upper + self.lower + self.digits + self.special,
				word_length
			):
				yield ''.join(word)

	def get_word(self) -> str:
		for word in (
			self._get_from_vocabulary
			if self.vocabulary
			else self._get_from_generator
		)():
			yield word

class ArchiveBrute(Brute):
	def get_password(self) -> None:
		for word in self.get_word():
			stdout = subprocess.call(
				# f"unzip -t -P {word} {self.filename}", # Pr0jects
				f"7z t -p'{word}' {self.target}",  # SECRET
				stderr=subprocess.DEVNULL,
				stdout=subprocess.DEVNULL,
				shell=True
			)
			if stdout == 0:
				self.password=word


def main():
	arc_brute = ArchiveBrute(target='../secure.7z')
	arc_brute.get_password()
	if arc_brute.password:
		print(f"Password found: {arc_brute.password}")

	else:
		print("Password not found.")

if __name__ == "__main__":
	main()
