from agents.newsletter_config_agent import NewsletterConfigAgent
agent = NewsletterConfigAgent()
print('Available domains count:', len(agent.get_available_domains()))
print('Default config:', agent.get_default_config().model_dump())
arts = agent.get_articles(enrich=False, use_selection=True)
print('Articles fetched:', len(arts))
for a in arts[:5]:
    print('-', getattr(a, 'title', 'no-title'))
