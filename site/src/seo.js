import React from "react";
import Helmet from "react-helmet";

const Seo = (props) => {
  const { siteUrl, title, description, imageUrl, twitterProfile = ''} = props;

  return (
    <Helmet>
      {/* General tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      {/* OpenGraph tags */}
      <meta name="og:url" content={siteUrl} />
      <meta name="og:title" content={title} />
      <meta name="og:description" content={description} />
      <meta name="og:image" content={imageUrl} />
      <meta name="og:type" content="website" />
      {/* Twitter Card tags */}
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={imageUrl} />
      <meta name="twitter:card" content="summary" />
      <meta name="twitter:creator" content={twitterProfile} />
    </Helmet>
  );
};

export default Seo;
