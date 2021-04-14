<script>
	import Lanes from "./Lanes.svelte";
	import About from "./About.svelte";
	import Contact from "./Contact.svelte";
	import Footer from "./Footer.svelte";
	import Header from "./Header.svelte";
	import Support from "./Support.svelte";

</script>

<main>
	<div class="maincontent">
		<Header />
		<h1>Pop the Bubble News</h1>
		<h5>
			A simple RSS feed dashboard to quickly view the full spectrum of
			news in the U.S.
		</h5>
		<Lanes />
	</div>
	<Support />
	<About />
	<Contact />
	<Footer />
</main>

<style>
	.maincontent {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
		background-color: transparent;
	}

	h1 {
		color: #111111;
		font-size: 2em;
		font-weight: 200;
	}

	h5 {
		color: #444444;
		font-size: 1em;
		font-weight: 200;
	}

	@media (min-width: 650px) {
		main {
			max-width: none;
		}
	}
</style>
