<script>
    export let article;
</script>

<!--
This tentatively just needs the article url, title, published_at, and the source's short name.
The article should be fetched from a parent component, so this should only accept the data and format it.
-->
<main>
    <div>
        <a href={article.url} target="_blank" rel="noopener noreferrer">{@html article.title}</a>
        {article.source.short_name}
        {article.published_at}
    </div>
</main>

<style>

</style>