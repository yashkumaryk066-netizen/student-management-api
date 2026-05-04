import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post
from django.utils.text import slugify
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the blog with SEO-optimized posts'

    def handle(self, *args, **kwargs):
        author = User.objects.filter(username='admin').first()
        if not author:
            author = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        posts_data = [
            {
                "title": "Top 10 Benefits of School Management Software in India (2026)",
                "excerpt": "Discover how school management systems are transforming education in India by automating attendance, fees, and exams.",
                "content": "<h2>Revolutionizing Indian Education with Technology</h2><p>In the rapidly evolving educational landscape of India, school management software has become a necessity rather than a luxury. From Naugachiya to Mumbai, schools are adopting AI-powered ERP systems to streamline their operations.</p><h3>1. Automated Fee Collection</h3><p>Gone are the days of long queues at the fee counter. With Y.S.M AI, parents can pay fees online via UPI or credit cards, and receipts are generated instantly.</p><h3>2. Smart Attendance Tracking</h3><p>Biometric and AI-based attendance systems ensure 100% accuracy and send real-time alerts to parents.</p><h3>3. Enhanced Teacher Productivity</h3><p>Teachers can now focus on teaching instead of administrative tasks like manual record-keeping.</p><p>Conclusion: Investing in a robust School ERP like Y.S.M AI is the best decision for any forward-thinking institution.</p>",
                "keywords": "School Management Software India, Best School ERP 2026, Education Technology Bihar"
            },
            {
                "title": "How to Grow Your Coaching Institute in 2026: The Ultimate Guide",
                "excerpt": "Learn the best strategies to scale your coaching center using lead management, automated batch scheduling, and AI analytics.",
                "content": "<h2>Scaling Your Coaching Business</h2><p>Competition in the coaching industry (JEE, NEET, UPSC) is at an all-time high. To stay ahead, you need more than just good teachers; you need the best coaching institute management software.</p><h3>Lead Management and Conversions</h3><p>Track every enquiry from start to finish. Our CRM module helps you convert potential students into admissions effectively.</p><h3>Batch Management</h3><p>Easily manage multiple batches, faculty schedules, and classroom allocations without any conflicts.</p><h3>Online Test Series</h3><p>Provide your students with a national-level testing experience with AI-powered auto-grading and performance analytics.</p>",
                "keywords": "Coaching Institute Management Software, Best Software for JEE Coaching, Institute Growth Tips"
            },
            {
                "title": "Why AI is the Future of School Administration",
                "excerpt": "Artificial Intelligence is no longer just for tech giants. Explore how AI-powered ERPs are helping schools predict student performance and optimize ROI.",
                "content": "<h2>The Rise of AI in Schools</h2><p>Y.S.M AI is at the forefront of the educational revolution. By integrating advanced AI models like ChatGPT and Gemini, we provide tools that were previously unimaginable.</p><h3>Predictive Analytics</h3><p>Identify students at risk of falling behind before it's too late. Our AI analyzes historical data to provide actionable insights.</p><h3>Automated Content Generation</h3><p>Teachers can generate lesson plans, quizzes, and summaries in seconds using our built-in AI tutor.</p><h3>ROI Intelligence</h3><p>Administrators can track the financial health of their institution with deep-dive ROI analytics.</p>",
                "keywords": "AI in Education, School ERP AI Features, Predictive Analytics for Students"
            },
            {
                "title": "Best ERP Software for Colleges and Universities in Bihar",
                "excerpt": "A comprehensive look at why colleges in Bhagalpur, Patna, and Katihar are switching to cloud-based management systems.",
                "content": "<h2>Modernizing Higher Education in Bihar</h2><p>Colleges in Bihar face unique challenges, from managing large student volumes to ensuring timely fee collection. Y.S.M AI provides a localized yet world-class solution.</p><h3>Campus Management</h3><p>Manage multiple departments, hostels, and libraries through a single dashboard.</p><h3>PWA Support</h3><p>Our system works offline and on low-bandwidth connections, making it perfect for rural areas like Rangra and Naugachiya.</p>",
                "keywords": "College Management Software Bihar, Best ERP Bhagalpur, University Management System"
            },
            {
                "title": "Streamlining Fee Management: A Case Study for Private Schools",
                "excerpt": "See how a private school reduced their fee defaults by 40% using automated reminders and online payment gateways.",
                "content": "<h2>The Fee Default Problem</h2><p>Many private schools struggle with late fee payments. Manual follow-ups are time-consuming and often ineffective.</p><h3>The Solution: Automated Alerts</h3><p>By sending automated WhatsApp and SMS alerts through Y.S.M AI, schools can ensure parents are reminded of upcoming due dates without manual intervention.</p><h3>Integration with ICICI Eazypay and Razorpay</h3><p>Secure and fast payment processing ensures that funds are settled into the school's account instantly.</p>",
                "keywords": "Automated Fee Management, School Fee Software India, Online Fee Collection"
            },
            {
                "title": "How to Conduct Online Exams with AI Proctoring",
                "excerpt": "Everything you need to know about setting up secure, cheat-proof online examinations for your students.",
                "content": "<h2>The Shift to Online Assessments</h2><p>Online exams are now a standard part of education. However, maintaining integrity is a challenge. Y.S.M AI's examination portal solves this.</p><h3>AI Proctoring</h3><p>Our system uses AI to detect suspicious behavior during exams, ensuring a fair testing environment.</p><h3>Instant Results</h3><p>Auto-grading for MCQs means students get their results immediately, and teachers save hours of manual marking.</p>",
                "keywords": "Online Exam Software, AI Proctoring for Schools, Automated Grading System"
            },
            {
                "title": "Smart Hostel Management: Beyond Just Room Allocation",
                "excerpt": "Optimize your hostel operations with biometric attendance, inventory tracking, and visitor management.",
                "content": "<h2>Effective Hostel Administration</h2><p>Managing a hostel involves more than just assigning rooms. It's about student safety and resource management.</p><h3>Biometric Security</h3><p>Ensure only authorized students enter the hostel with integrated biometric systems.</p><h3>Inventory and Mess Management</h3><p>Track food stock and manage mess bills effortlessly within the same ERP.</p>",
                "keywords": "Hostel Management System, Smart School Hostel, Mess Management Software"
            },
            {
                "title": "Improving Parent-Teacher Communication in 2026",
                "excerpt": "Discover how a dedicated mobile app and real-time notifications can build trust between parents and schools.",
                "content": "<h2>Bridging the Communication Gap</h2><p>Parents want to be involved in their child's education. Traditional diaries are outdated. The Y.S.M AI Parent App provides instant updates.</p><h3>Real-time Notifications</h3><p>From homework assignments to emergency alerts, keep parents informed instantly via push notifications.</p><h3>Transparency</h3><p>Parents can track their child's attendance and performance history at any time, reducing the need for frequent physical meetings.</p>",
                "keywords": "Parent Teacher Communication App, School Notification System, Best School App India"
            },
            {
                "title": "The Role of a Software Developer in Naugachiya's Tech Growth",
                "excerpt": "A deep dive into how local developers like Yash Ankush Mishra are putting Naugachiya and Rangra on the global tech map.",
                "content": "<h2>Tech Innovation in Rural Bihar</h2><p>Naugachiya and Rangra are becoming hubs for software development. The creation of Y.S.M AI is a testament to the talent available in our region.</p><h3>Building for the World</h3><p>Our software is designed with global standards, serving clients from local coaching centers to international schools.</p><h3>Empowering Local Businesses</h3><p>By providing affordable tech solutions, we are helping local businesses digitize and compete on a national level.</p>",
                "keywords": "Software Developer Naugachiya, Best Developer Bihar, Yash Ankush Mishra Tech"
            },
            {
                "title": "Why Your Coaching Center Needs a Mobile App",
                "excerpt": "In 2026, having a website is not enough. Learn why a mobile app is crucial for student engagement and brand building.",
                "content": "<h2>The Mobile-First Student</h2><p>Students today are always on their phones. A dedicated mobile app ensures that your coaching brand is always just a tap away.</p><h3>Offline Access to Study Materials</h3><p>Our PWA-enabled app allows students to download notes and videos for offline viewing.</p><h3>Push Notifications for Flash Sales</h3><p>Run promotions and announce new batches directly to your students' phones for maximum reach.</p>",
                "keywords": "Coaching Center Mobile App, Best App for Coaching Institute, Student Engagement App"
            }
        ]

        # Generate more variations to reach a higher count
        all_posts = []
        for i in range(5): # Create 50 posts by repeating and slightly modifying the 10 templates
            for data in posts_data:
                suffix = f" (Edition {i+1})" if i > 0 else ""
                p = Post(
                    title=data['title'] + suffix,
                    slug=slugify(data['title'] + suffix),
                    author=author,
                    content=data['content'],
                    excerpt=data['excerpt'],
                    meta_title=data['title'],
                    meta_description=data['excerpt'],
                    meta_keywords=data['keywords'],
                    status='published',
                    published_date=timezone.now() - timezone.timedelta(days=random.randint(0, 100))
                )
                all_posts.append(p)
        
        Post.objects.bulk_create(all_posts, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(all_posts)} blog posts'))
