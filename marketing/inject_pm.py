import subprocess
import time

msg = """আসসালামু আলাইকুম শ্রদ্ধেয় স্যার/ম্যাম,
মল্লিক বিল্ডার্স লিমিটেডের পক্ষ থেকে আন্তরিক শুভেচ্ছা।

আমাদের 'প্রজেক্ট ১০' (বাশতলা, ভুঁইয়া বাড়ি - উত্তরা আজমপুর থেকে ১০ মিনিট) এর আকর্ষণীয় ফ্ল্যাট বুকিং ও বিস্তারিত তথ্য:

🏢 ফ্ল্যাট সাইজ: ১৫৭০ স্কয়ার ফিট গ্রস (১২৫০ স্কয়ার ফিট নেট ইউজেবল এরিয়া), ৩ বেড, ৩ বাথ, ২ বারান্দা, ড্রয়িং-ডাইনিং ও কিচেন।
🏗️ সুবিধা: ৮.৭২ কাঠায় G+9 আধুনিক কন্ডো, ২টি হাই-স্পিড লিফট, নিজস্ব মসজিদ ও ৫,০০০ স্কয়ার ফিট রুফটপ গার্ডেন।

💰 মূল্য ও কিস্তি:
• জমি শেয়ার: মাত্র ১২ লাখ টাকা
• নির্মাণ ব্যয়: ৩৬.২৫ লাখ টাকা
• সর্বমোট প্যাকেজ: মাত্র ৪৮.২৫ লাখ টাকা (৩৬ মাসের সহজ কিস্তির সুবিধা)
• সময়মতো হস্তান্তরের নিশ্চয়তা ও ক্ষতিপূরণ ভাড়ার চুক্তি!

🗓️ সরাসরি সাইট পরিদর্শন ও বুকিংয়ের জন্য যোগাযোগ করুন:
📞 কল বা হোয়াটসঅ্যাপ: 01633-309081 / 01805-892106
(আপনার ফোন নাম্বারটি জানালে আমাদের সিনিয়র প্রতিনিধি আপনার সাথে সরাসরি যোগাযোগ করবেন।)"""

# Copy to macOS clipboard
p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
p.communicate(msg.encode("utf-8"))

# Run AppleScript to focus Draft.js editor and paste
osa = '''tell application "Brave Browser"
    activate
    execute active tab of window 1 javascript "document.querySelectorAll('div[contenteditable=true]')[0].focus(); document.execCommand('selectAll', false, null);"
end tell
delay 0.3
tell application "System Events"
    keystroke "v" using command down
end tell
'''

subprocess.run(["osascript", "-e", osa])
print("Successfully pasted into Draft.js Private Message editor!")

