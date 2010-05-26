import settings

ga_html = """<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("%s");
pageTracker._trackPageview();
} catch(err) {}</script></body>
"""

class GoogleAnalyticsMiddleware:
    def process_response(self, request, response):
        ga_id = settings.GOOGLE_ANALYTICS_ID
        if ga_id:
            current = response.content
            replacement = ga_html % ga_id
            response.content = current.replace("</body>", replacement)
        return response
