---
layout: post  
title: "5 CSS Selectors You Didn’t Know You Needed"  
date: 2025-03-21  
categories: [Developer Tools, Web Development, CSS]  
tags: [CSS, Developer Tools, Cheat Sheet, Programming, Frontend]  
author: Teki Solves  
author_url: https://tekisolves.github.io  
---

## 5 CSS Selectors You Didn’t Know You Needed

<img src="/css-selector-cheat-sheet-cover-2.jpg" class="img-fluid"/>

Ever feel like your CSS could be sharper, more efficient, and downright smarter?  
Here are five underused CSS selectors that can transform how you style your web pages:

### 1. The Attribute Contains Word Selector `[attr~="value"]`
This selector finds elements whose attribute value contains a specific word. Perfect for multi-word class names or attributes.
```css
input[type~="email"] {
  border: 2px solid #43a047;
}
```
Save time by avoiding complex class juggling and targeting exactly what you need.

### 2. The Attribute Begins With Selector `[attr|="value"]`
Great for styling elements where attributes follow a structured pattern (like language codes).
```css
[lang|="en"] {
  font-family: sans-serif;
}
```
Quickly style elements that share a common prefix in their attribute values.


### 3. The Negation Pseudo-Class `:not()`
Exclude specific elements from styling without adding extra markup.
```css
.button:not(.disabled) {
  background-color: #1e88e5;
}
```
Streamline your CSS by leaving out unwanted targets.

### 4. The General Sibling Combinator `E ~ F`
Select all sibling elements that follow a certain element.
```css
h2 ~ p {
  margin-top: 0;
}
```
Keep layouts dynamic and uncluttered without unnecessary HTML complexity.


### 5. The Advanced Pseudo-Class Combo `:nth-child()`
Combine `:nth-child()` with other pseudo-classes for dynamic styling magic.
```css
li:nth-child(odd):hover {
  background-color: #f5f5f5;
}
```
Add interactivity and polished design touches with minimal code.


### Take It Further with the Teki Solves Cheat Sheet

These five selectors are just the start. If you're ready to level up your CSS game, grab the **Teki Solves Advanced CSS Selector Cheat Sheet** — packed with in-depth explanations, real-world examples, and best practices to help you write cleaner, more powerful CSS.

[Download the CSS Selector Cheat Sheet Now](https://tekisolve.gumroad.com/l/grjet)

Keep it simple, solve the problem, and write CSS like a pro.