import subprocess

msg = """আসসালামু আলাইকুম! মল্লিক বিল্ডার্স লিমিটেডে স্বাগতম।

উত্তরা আজমপুর সংলগ্ন 'প্রজেক্ট ১০' (বাশতলা, ভুঁইয়া বাড়ি)-এ ১৫৭০ স্কয়ার ফিট ৩-বেড বিলাসবহুল ফ্ল্যাট বুকিং চলছে!

💰 জমি শেয়ার মাত্র ১২ লাখ + নির্মাণ ৩৬.২৫ লাখ = সর্বমোট ৪৮.২৫ লাখ টাকা (৩৬ মাসের সহজ কিস্তিতে পরিশোধযোগ্য)।

সরাসরি পেপারস যাচাই ও সাইট ভিজিটের জন্য আপনার ফোন নাম্বারটি জানান অথবা এখনই কল করুন:
📞 01633-309081 / 01805-892106
আমাদের প্রতিনিধি দ্রুত যোগাযোগ করবেন।"""

p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
p.communicate(msg.encode("utf-8"))

osa = '''tell application "Brave Browser"
    activate
    set active tab index of window 1 to 2
    execute active tab of window 1 javascript "const d = document.querySelector('div[contenteditable=true]'); if (d) { d.focus(); document.execCommand('selectAll', false, null); }"
end tell
delay 0.3
tell application "System Events"
    keystroke "v" using command down
end tell
'''

subprocess.run(["osascript", "-e", osa])
print("Pasted instant reply copy!")

