<script>
	import Lane from './Lane.svelte';

</script>

<main>
	<h1>News Dashboard</h1>
	<div>
		<Lane rssUrl="https://www.vox.com/rss/index.xml"/>
		<Lane rssUrl="https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"/>
		<Lane rssUrl="http://www.npr.org/rss/rss.php?id=1001"/>
		<Lane rssUrl="http://feeds.foxnews.com/foxnews/national"/>
		<Lane rssUrl="http://feeds.feedburner.com/breitbart"/>
	</div>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
	}

	div {
		display: flex;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>